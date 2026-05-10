# Security Policy

## Reporting a vulnerability

If you find a security issue in MissedRun Self-hosted, please do not open a public GitHub issue with sensitive details.

Instead, contact:

contact@missedrun.com

Please include:

- a short description of the issue
- affected endpoint or component
- steps to reproduce
- potential impact
- suggested fix, if you have one

## Secrets

Do not commit secrets to this repository.

This includes:

- `.env` files
- SMTP passwords
- database passwords
- API keys
- GitHub tokens
- monitor ping tokens

Ping tokens should be treated as secrets. Anyone with a monitor token can send pings for that monitor.

## Supported versions

This project is currently in early development. Security fixes will be applied to the `main` branch.
