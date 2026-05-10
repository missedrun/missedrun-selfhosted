# MissedRun Self-hosted

MissedRun Self-hosted is a small open-source monitor for cron jobs, scheduled scripts, backups, imports, ETL jobs, and recurring background tasks.

It detects silent failures by expecting each job to check in on time.

If a job does not report back within its expected interval plus grace period, MissedRun marks it as missing and can send an alert.

## Why?

Some failures are silent:

- a cron job does not run
- a server is down
- a Docker container stops
- credentials expire
- a backup script never starts
- an ETL job stops updating data
- a scheduled report is not generated

MissedRun is built for that situation.

## Features

- Create monitors for scheduled jobs
- Generate unique ping URLs
- Record successful check-ins
- Record job start events
- Record job failure events
- Track monitor status: pending, running, healthy, failed, missing, paused
- Store event history
- Background checker for missing jobs
- Docker Compose setup
- Basic email alert support

## Quick start

1. Copy the environment file:

    cp .env.example .env

2. Start the services:

    docker compose up -d

3. Check the API:

    curl http://localhost:8008/health

4. Check the database:

    curl http://localhost:8008/db-health

## Create a monitor

    curl -X POST http://localhost:8008/api/monitors \
      -H "Content-Type: application/json" \
      -d '{
        "name": "Nightly backup",
        "interval_minutes": 1440,
        "grace_minutes": 60
      }'

The response includes a token.

## Send a success ping

    curl -X POST http://localhost:8008/api/ping/YOUR_TOKEN

## Send a start ping

Use this when a job starts running:

    curl -X POST http://localhost:8008/api/ping/YOUR_TOKEN/start

## Send a failure ping

Use this when a job fails:

    curl -X POST http://localhost:8008/api/ping/YOUR_TOKEN/fail \
      -H "Content-Type: application/json" \
      -d '{"message":"Backup failed"}'

## List monitors

    curl http://localhost:8008/api/monitors

## View monitor history

    curl http://localhost:8008/api/monitors/1/history

## Environment variables

Copy .env.example to .env and edit the values.

Main variables:

    DATABASE_URL=postgresql://missedrun:missedrun@postgres:5432/missedrun
    ALERT_EMAIL=
    SMTP_HOST=
    SMTP_PORT=587
    SMTP_USERNAME=
    SMTP_PASSWORD=
    SMTP_FROM_EMAIL=

If SMTP is not configured, alerts are printed in the container logs.

## Hosted version

Prefer not to self-host?

A hosted version is available at:

https://missedrun.com

## License

License to be decided.
