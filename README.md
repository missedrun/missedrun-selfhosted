# MissedRun Self-hosted

Self-hosted cron and scheduled job monitoring for detecting silent failures.

Hosted version: https://missedrun.com  
Self-hosted version: https://github.com/missedrun/missedrun-selfhosted

MissedRun monitors recurring jobs such as cron scripts, backups, imports, ETL pipelines, billing syncs, cleanup tasks, and scheduled reports.

It works by giving each monitor a unique ping URL. Your job calls that URL when it runs. If the job does not check in within the expected interval plus grace period, MissedRun marks it as missing and can send an alert.

## Why MissedRun?

Some production failures are not loud.

A job can stop running without throwing an exception:

- cron did not run
- a server was down
- a Docker container stopped
- credentials expired
- a backup script never started
- an ETL job stopped updating data
- a scheduled report was not generated
- a background worker silently stopped

MissedRun is built to detect this kind of silent failure.

## Features

- Create monitors for scheduled jobs
- Generate unique ping URLs
- Record successful check-ins
- Record job start events
- Record explicit failure events
- Track monitor status:
  - pending
  - running
  - healthy
  - failed
  - missing
  - paused
- Store event history
- Background checker for missing jobs
- Basic email alert support
- Docker Compose setup
- FastAPI backend
- PostgreSQL storage

## Hosted vs self-hosted

This repository contains the self-hosted version of MissedRun.

Use the self-hosted version if you want to run the monitor on your own infrastructure.

Use the hosted version if you want MissedRun without managing servers, updates, SMTP, database backups, or deployment.

Hosted version:

https://missedrun.com

## Quick start

Clone the repository:

    git clone https://github.com/missedrun/missedrun-selfhosted.git
    cd missedrun-selfhosted

Copy the example environment file:

    cp .env.example .env

Start the services:

    docker compose up -d

Check the API:

    curl http://localhost:8008/health

Check the database:

    curl http://localhost:8008/db-health

## Create a monitor

    curl -X POST http://localhost:8008/api/monitors \
      -H "Content-Type: application/json" \
      -d '{
        "name": "Nightly backup",
        "interval_minutes": 1440,
        "grace_minutes": 60
      }'

The response includes a `token`.

Example response:

    {
      "id": 1,
      "name": "Nightly backup",
      "token": "YOUR_MONITOR_TOKEN",
      "interval_minutes": 1440,
      "grace_minutes": 60,
      "status": "pending"
    }

## Ping a monitor

Send a success ping when the job finishes successfully:

    curl -X POST http://localhost:8008/api/ping/YOUR_MONITOR_TOKEN

Example cron usage:

    0 2 * * * /usr/local/bin/backup.sh && curl -X POST http://localhost:8008/api/ping/YOUR_MONITOR_TOKEN

## Start ping

Use a start ping when a job begins running:

    curl -X POST http://localhost:8008/api/ping/YOUR_MONITOR_TOKEN/start

This changes the monitor status to `running`.

## Failure ping

Use a failure ping when a job fails:

    curl -X POST http://localhost:8008/api/ping/YOUR_MONITOR_TOKEN/fail \
      -H "Content-Type: application/json" \
      -d '{"message":"Backup failed"}'

This changes the monitor status to `failed` and records the failure message.

## List monitors

    curl http://localhost:8008/api/monitors

## View monitor history

    curl http://localhost:8008/api/monitors/1/history

## Statuses

MissedRun uses these monitor statuses:

| Status | Meaning |
|---|---|
| pending | The monitor was created but has not received a ping yet |
| running | The job has sent a start ping |
| healthy | The last success ping was received on time |
| failed | The job explicitly reported a failure |
| missing | The job did not check in within the expected time |
| paused | The monitor is paused and will not alert |

## Environment variables

Copy `.env.example` to `.env` and edit the values.

Main variables:

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

If SMTP is not configured, alerts are printed in the container logs.

## Development

Start the stack:

    docker compose up -d

View logs:

    docker compose logs -f backend
    docker compose logs -f checker

Stop the stack:

    docker compose down

Reset the local database volume:

    docker compose down -v

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /health | API health check |
| GET | /db-health | Database health check |
| POST | /api/monitors | Create a monitor |
| GET | /api/monitors | List monitors |
| GET | /api/monitors/{id} | Get a monitor |
| PATCH | /api/monitors/{id} | Update a monitor |
| DELETE | /api/monitors/{id} | Delete a monitor |
| POST | /api/monitors/{id}/pause | Pause a monitor |
| POST | /api/monitors/{id}/resume | Resume a monitor |
| GET | /api/monitors/{id}/history | View monitor history |
| POST | /api/ping/{token} | Success ping |
| POST | /api/ping/{token}/start | Start ping |
| POST | /api/ping/{token}/fail | Failure ping |

## Roadmap

Possible next features:

- Web dashboard
- Webhook alerts
- Slack alerts
- Discord alerts
- Telegram alerts
- Better Docker images
- Authentication for shared deployments
- Metrics and uptime summaries
- Public status pages

## Security

Do not commit your `.env` file.

Ping tokens should be treated as secrets. Anyone with a monitor token can send pings for that monitor.

## License

MissedRun Self-hosted is licensed under the GNU Affero General Public License v3.0.

See the `LICENSE` file for details.
