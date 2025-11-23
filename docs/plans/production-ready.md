# Plan: Production-Ready Docker Deployment (Scaleway 2GB)

## Phase 1: Critical Fixes & Scaleway Optimization ✅

- [x] Fix MEDIA configuration in backend settings
- [x] Create .env.example with Brevo/Sentry/all vars
- [x] Add SSL/HTTPS Nginx + Certbot configs
- [x] Django security settings (SECURE_*, HSTS, CSRF, SESSION)
- [x] Sentry integration for Django error tracking
- [x] Brevo SMTP configuration via env vars
- [x] PostgreSQL tuning for 2GB RAM (shared_buffers=256MB, work_mem, connections)
- [x] Mount logs properly (/var/log/nginx/, backend logs with rotation)
- [x] Docker resource limits (prevent OOM on 2GB)
- [x] Gunicorn workers tuning (2 workers max for 2GB RAM)
- [x] Verify frontend Dockerfile has Nginx serving React + reverse proxy to backend

## Phase 2: Deployment documentation ✅

- [x] VPS Setup Guide (docs/deployment/vps-setup.md):
  - Scaleway VPS-START-S provisioning
  - SWAP activation (2GB swap file)
  - DNS configuration walkthrough
  - Docker install + initial server hardening
  - SSL certificate (Certbot + auto-renewal)
  - Storage cleanup commands (prune old images/containers)

- [x] Build & Registry Workflow (docs/deployment/build-and-deploy.md):
  - Build frontend/backend LOCALLY
  - Push to GitHub Container Registry (ghcr.io)
  - Pull & deploy on VPS
  - Storage management: docker system prune -a --filter "until=168h"

- [x] Environment Config Guide (docs/deployment/environment-config.md) with all vars (Brevo, Sentry, DB, etc.)

## Phase 3: Backups & Monitoring ✅

- [x] Automated backup script with retention (scripts/backup.sh, scripts/restore.sh):
  - Daily: 7 days
  - Weekly: 4 weeks
  - Monthly: 1 month
  - Offsite copy (Scaleway Object Storage)
  - Backup documentation (docs/deployment/backups.md)

- [x] Monitoring setup docs (docs/deployment/monitoring.md):
  - [x] Sentry Django integration
  - [x] UptimeRobot/BetterStack HTTP checks
  - [x] Log rotation (7 daily, 4 weekly, 1 monthly)

- [x] Nginx hardening: rate limiting, gzip, security headers, client_max_body_size

## Phase 4: Production Hardening ✅

- [x] Healthcheck endpoints (/api/health/)
- [x] Database connection pooling tuning
- [x] Production checklist with verification steps
- [x] Disaster recovery runbook

## Deliverables

 - Scaleway-optimized setup (2GB RAM, 2GB SWAP, storage-conscious)
 - GitHub Container Registry workflow
 - Complete VPS guide (SWAP, DNS, SSL, storage mgmt)
 - Backup automation (7/4/1 retention)
 - Brevo + Sentry + UptimeRobot/BetterStack integration
 - Docker cleanup automation to prevent storage exhaustion
