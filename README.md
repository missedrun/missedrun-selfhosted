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
