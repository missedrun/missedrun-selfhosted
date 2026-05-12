# MissedRun Self-hosted

Self-hosted cron and scheduled job monitoring for detecting silent failures.

MissedRun monitors recurring jobs such as cron scripts, backups, imports, ETL pipelines, billing syncs, cleanup tasks, and scheduled reports.

It works by giving each monitor a unique ping URL. Your job calls that URL when it runs, starts, finishes successfully, or fails. If the job does not check in within the expected interval plus grace period, MissedRun marks it as missing and can send an alert.

* Hosted version: [https://missedrun.com](https://missedrun.com)
* Self-hosted version: [https://github.com/missedrun/missedrun-selfhosted](https://github.com/missedrun/missedrun-selfhosted)
* License: AGPL-3.0

## What problem does it solve?

Some production failures are not loud.

A job can stop running without throwing an exception. For example:

* cron did not run
* the server was down
* a Docker container stopped
* credentials expired before the job reached your alerting code
* a backup script never started
* an import stopped updating data
* a scheduled report was not generated
* a background worker silently stopped

MissedRun is built to detect this kind of silent failure.

## Current V1 features

This repository is the V1 self-hosted version. It currently focuses on basic heartbeat-style monitoring for scheduled jobs.

Available now:

* Create monitors for scheduled jobs
* Generate unique ping URLs
* Success ping endpoint
* Optional start ping endpoint
* Optional failure ping endpoint
* Track monitor status:
  * pending
  * running
  * healthy
  * failed
  * missing
  * paused
* Store monitor event history
* Background checker for missing jobs
* Basic email alert support
* Docker Compose setup
* FastAPI backend
* PostgreSQL storage

Not included in V1:

* Slack alerts
* Webhook alerts
* Discord alerts
* Telegram alerts
* Teams / workspaces
* Output metrics such as processed count, created count, or failed count
* Rules/assertions on job output
* Anomaly detection
* Historical volume comparison
* Public status pages
* Integration marketplace

## Screenshots

### Dashboard

![MissedRun dashboard](docs/screenshots/dashboard.webp)

### Monitor details and history

![MissedRun monitor details and history](docs/screenshots/monitor-history.webp)

### Ping URLs

![MissedRun ping URLs](docs/screenshots/ping-urls.webp)

### Create monitor

![Create a MissedRun monitor](docs/screenshots/create-monitor.webp)

### Email alert

![MissedRun email alert](docs/screenshots/email-alert.webp)

## Hosted vs self-hosted

This repository contains the self-hosted version of MissedRun.

Use the self-hosted version if you want to run the monitor on your own infrastructure.

Use the hosted version if you want MissedRun without managing servers, updates, SMTP, database backups, or deployment.

Hosted version: [https://missedrun.com](https://missedrun.com)

## Quick start

Clone the repository:

```bash
git clone https://github.com/missedrun/missedrun-selfhosted.git
cd missedrun-selfhosted
```

Copy the example environment file:

```bash
cp .env.example .env
```

Start the services:

```bash
docker compose up -d
```

Check the API:

```bash
curl http://localhost:8008/health
```

Check the database:

```bash
curl http://localhost:8008/db-health
```

## Create a monitor

Create a monitor for a nightly backup that should run once every 24 hours, with a 60-minute grace period:

```bash
curl -X POST http://localhost:8008/api/monitors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nightly backup",
    "interval_minutes": 1440,
    "grace_minutes": 60
  }'
```

The response includes a `token`:

```json
{
  "id": 1,
  "name": "Nightly backup",
  "token": "YOUR_MONITOR_TOKEN",
  "interval_minutes": 1440,
  "grace_minutes": 60,
  "status": "pending"
}
```

## Ping a monitor

Send a success ping when the job finishes successfully:

```bash
curl -X POST http://localhost:8008/api/ping/YOUR_MONITOR_TOKEN
```

Example cron usage:

```cron
0 2 * * * /usr/local/bin/backup.sh && curl -fsS -X POST http://localhost:8008/api/ping/YOUR_MONITOR_TOKEN
```

## Recommended wrapper script

For real jobs, it is better to report start, success, and failure:

```bash
#!/usr/bin/env bash
set -u

PING_BASE="http://localhost:8008/api/ping/YOUR_MONITOR_TOKEN"

curl -fsS -X POST "$PING_BASE/start" >/dev/null || true

if /usr/local/bin/backup.sh; then
  curl -fsS -X POST "$PING_BASE" >/dev/null || true
else
  curl -fsS -X POST "$PING_BASE/fail" \
    -H "Content-Type: application/json" \
    -d '{"message":"Backup failed"}' >/dev/null || true
  exit 1
fi
```

Then run the wrapper from cron:

```cron
0 2 * * * /usr/local/bin/monitored-backup.sh
```

## Start ping

Use a start ping when a job begins running:

```bash
curl -X POST http://localhost:8008/api/ping/YOUR_MONITOR_TOKEN/start
```

This changes the monitor status to `running`.

## Failure ping

Use a failure ping when a job fails:

```bash
curl -X POST http://localhost:8008/api/ping/YOUR_MONITOR_TOKEN/fail \
  -H "Content-Type: application/json" \
  -d '{"message":"Backup failed"}'
```

This changes the monitor status to `failed` and records the failure message.

## List monitors

```bash
curl http://localhost:8008/api/monitors
```

## View monitor history

```bash
curl http://localhost:8008/api/monitors/1/history
```

## Statuses

| Status    | Meaning                                                                  |
| --------- | ------------------------------------------------------------------------ |
| `pending` | The monitor was created but has not received a ping yet.                 |
| `running` | The job sent a start ping and has not completed yet.                     |
| `healthy` | The last success ping was received on time.                              |
| `failed`  | The job explicitly reported a failure.                                   |
| `missing` | The job did not check in within the expected interval plus grace period. |
| `paused`  | The monitor is paused and will not alert.                                |

## Environment variables

Copy `.env.example` to `.env` and edit the values.

```env
APP_NAME=MissedRun Self-hosted
APP_ENV=development
DATABASE_URL=postgresql://missedrun:missedrun@postgres:5432/missedrun
BACKEND_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

ALERT_EMAIL=

SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=
SMTP_FROM_NAME=MissedRun
SMTP_REPLY_TO=
```

If SMTP is not configured, alerts are printed in the container logs.

## Development

Start the stack:

```bash
docker compose up -d
```

View logs:

```bash
docker compose logs -f backend
docker compose logs -f checker
```

Stop the stack:

```bash
docker compose down
```

Reset the local database volume:

```bash
docker compose down -v
```

## API endpoints

| Method   | Endpoint                     | Description           |
| -------- | ---------------------------- | --------------------- |
| `GET`    | `/health`                    | API health check      |
| `GET`    | `/db-health`                 | Database health check |
| `POST`   | `/api/monitors`              | Create a monitor      |
| `GET`    | `/api/monitors`              | List monitors         |
| `GET`    | `/api/monitors/{id}`         | Get a monitor         |
| `PATCH`  | `/api/monitors/{id}`         | Update a monitor      |
| `DELETE` | `/api/monitors/{id}`         | Delete a monitor      |
| `POST`   | `/api/monitors/{id}/pause`   | Pause a monitor       |
| `POST`   | `/api/monitors/{id}/resume`  | Resume a monitor      |
| `GET`    | `/api/monitors/{id}/history` | View monitor history  |
| `POST`   | `/api/ping/{token}`          | Success ping          |
| `POST`   | `/api/ping/{token}/start`    | Start ping            |
| `POST`   | `/api/ping/{token}/fail`     | Failure ping          |

## Security

Do not commit your `.env` file.

Ping tokens should be treated as secrets. Anyone with a monitor token can send pings for that monitor.

For public or shared deployments, run MissedRun behind HTTPS and restrict access to the API/dashboard as needed.

## License

MissedRun Self-hosted is licensed under the GNU Affero General Public License v3.0.

See the `LICENSE` file for details.
