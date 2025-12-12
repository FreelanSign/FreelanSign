# RGPD Retention Policy - Deployment Guide

**Feature**: Automated GDPR-compliant data retention and purge system
**Version**: 0.2.0
**Issue**: [#72](https://github.com/FreelanSign/FreelanSign/issues/72)
**Status**: ✅ Ready for Production

---

## Table of Contents

1. [Overview](#overview)
2. [Legal Compliance](#legal-compliance)
3. [Configuration](#configuration)
4. [Deployment](#deployment)
5. [Testing](#testing)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)
8. [Rollback Strategy](#rollback-strategy)

---

## Overview

The RGPD retention policy automates data purge to comply with GDPR Article 5(1)(e) storage limitation:

- **AuditLog**: Purges records older than 13 months (395 days) - CNIL recommendation
- **Soft-deleted Accounts/Clients**: Hard deletes records older than 10 years - French accounting law

**Safety Guardrails:**
- Protects accounting data with active or recent quotes (< 10 years)
- Transaction rollback on any error
- Sentry alerting on failures

**Schedule**: Weekly execution (Sunday 3:00 AM)

---

## Legal Compliance

### Retention Periods

| Data Type | Retention Period | Legal Basis |
|-----------|-----------------|-------------|
| **Audit Logs** | 13 months (395 days) | CNIL recommendation |
| **Soft-deleted Accounts** | 10 years | French accounting law (CGI Art. L.102 B) |
| **Soft-deleted Clients** | 10 years | French accounting law |
| **Active Accounts/Clients** | Indefinite | User consent (service usage) |
| **Quotes (all statuses)** | 10 years (protected) | Accounting law |

### References

- **GDPR Art. 5(1)(e)**: Storage limitation principle
- **CNIL Recommendation**: 13 months for audit/security logs
- **French Accounting Law**: CGI Art. L.102 B (10-year retention)
- **Project Spec**: `/SPECIFICATIONS_RGPD.md` Section 3.4

---

## Configuration

### Environment Variables

Add to `.env` (production):

```bash
# RGPD Retention Policy Configuration
# CRITICAL: Must be explicitly enabled in production
RETENTION_POLICY_ENABLED=True

# Retention periods (optional - defaults shown)
RETENTION_AUDIT_LOGS_DAYS=395      # 13 months
RETENTION_ACCOUNTING_YEARS=10       # 10 years

# Sentry (for alerting)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
```

### Django Settings

Already configured in `/backend/config/settings.py`:

```python
RETENTION_POLICY_ENABLED = env.bool('RETENTION_POLICY_ENABLED', default=False)
RETENTION_AUDIT_LOGS_DAYS = env.int('RETENTION_AUDIT_LOGS_DAYS', default=395)
RETENTION_ACCOUNTING_YEARS = env.int('RETENTION_ACCOUNTING_YEARS', default=10)
```

**Default**: Policy is **DISABLED** (fail-safe). Must be explicitly enabled.

---

## Deployment

### Prerequisites

- [x] SoftDeleteModel implementation (Account, Client) - ✅ PR #68
- [x] AuditLog model - ✅ PR #71
- [x] Docker Compose production setup
- [x] Sentry integration

### Deployment Steps

#### 1. Deploy Code

```bash
# Merge PR to main branch
git checkout main
git merge feat/rgpd-retention-policy

# Build Docker image
docker build -t ghcr.io/freelansign/freelansign-backend:latest ./backend

# Push to registry
docker push ghcr.io/freelansign/freelansign-backend:latest
```

#### 2. Update Environment Variables

On production server:

```bash
# Edit .env file
nano /path/to/.env

# Add:
RETENTION_POLICY_ENABLED=True
RETENTION_AUDIT_LOGS_DAYS=395
RETENTION_ACCOUNTING_YEARS=10
```

#### 3. Deploy CRON Container

```bash
# Deploy updated docker-compose.prod.yml
cd /path/to/FreelanSign
docker-compose -f docker-compose.prod.yml up -d

# Verify CRON container is running
docker ps | grep freelansign_cron_prod

# Check CRON schedule
docker exec freelansign_cron_prod crontab -l
# Expected output: 0 3 * * 0 cd /app && python manage.py apply_retention_policy >> /app/logs/retention_policy.log 2>&1
```

#### 4. Verify Deployment

```bash
# Check container health
docker exec freelansign_cron_prod echo "CRON container is healthy"

# Check logs directory exists
docker exec freelansign_cron_prod ls -la /app/logs

# Verify database connectivity
docker exec freelansign_cron_prod python manage.py check
```

---

## Testing

### Pre-Production Testing

#### 1. Dry-Run Mode (Staging)

**CRITICAL**: Always run dry-run FIRST in production before live purge.

```bash
# SSH to production server
ssh user@your-server.com

# Run dry-run (shows what WOULD be deleted, no changes)
docker exec freelansign_backend_prod python manage.py apply_retention_policy --dry-run

# Expected output:
# 🔄 Starting retention policy (DRY-RUN mode)...
# 🗑️  Purging X AuditLog records older than YYYY-MM-DD...
# ✅ No soft-deleted Accounts older than 10 years
# ✅ No soft-deleted Clients older than 10 years
# 🔄 Dry-run complete - no database changes made (transaction rolled back)
# 📊 Summary:
#   - AuditLog records purged: X
#   - Accounts purged: 0
#   - Clients purged: 0
#   - Total records deleted: X
```

#### 2. Force Mode (Development)

For testing in development environment:

```bash
# Development mode (policy disabled by default)
python manage.py apply_retention_policy --force

# Or with dry-run
python manage.py apply_retention_policy --dry-run --force
```

### Post-Deployment Validation

#### 1. Monitor First CRON Execution

**Schedule**: Sunday at 3:00 AM (first week after deployment)

```bash
# Sunday 3:05 AM - Check logs
docker exec freelansign_cron_prod cat /app/logs/retention_policy.log

# Expected log entries:
# [timestamp] 🔄 Starting retention policy (PRODUCTION mode)...
# [timestamp] 🗑️  Purging X AuditLog records older than [date]...
# [timestamp] ✅ Retention policy applied successfully
# [timestamp] 📊 Summary: ...
```

#### 2. Verify Purge Results

```bash
# Connect to Django shell
docker exec -it freelansign_backend_prod python manage.py shell

# Check AuditLog count (should be reduced)
>>> from apps.core.models.audit import AuditLog
>>> from datetime import timedelta
>>> from django.utils import timezone
>>> cutoff = timezone.now() - timedelta(days=395)
>>> old_logs = AuditLog.objects.filter(timestamp__lt=cutoff).count()
>>> print(f"Old logs remaining: {old_logs}")  # Should be 0
```

#### 3. Check Sentry Alerts

- Go to Sentry dashboard
- Verify NO errors during first purge
- Check for warning alerts if purge count > 1000

---

## Monitoring

### Sentry Alerts

**Alert Scenarios:**

1. **Purge Failure** (Error level)
   - Triggered on: Any exception during purge
   - Contains: Full stacktrace, error context
   - Action: Investigate logs, check database connectivity

2. **High Purge Count** (Warning level)
   - Triggered on: > 1000 records purged in single run
   - Contains: Breakdown by model (AuditLog, Account, Client)
   - Action: Review if expected, investigate if anomalous

3. **Policy Disabled in Production** (Error level)
   - Triggered on: Attempting to run with `RETENTION_POLICY_ENABLED=False`
   - Action: Enable policy or document exception

### Log Monitoring

**Log File**: `/app/logs/retention_policy.log`

```bash
# View recent logs
docker exec freelansign_cron_prod tail -100 /app/logs/retention_policy.log

# Monitor logs in real-time (during manual run)
docker exec freelansign_cron_prod tail -f /app/logs/retention_policy.log
```

**Success Log Format:**
```
🔄 Starting retention policy (PRODUCTION mode)...
🗑️  Purging X AuditLog records older than YYYY-MM-DD...
✅ No soft-deleted Accounts older than 10 years
✅ No soft-deleted Clients older than 10 years
✅ Retention policy applied successfully
📊 Summary:
  - AuditLog records purged: X
  - Accounts purged: 0
  - Clients purged: 0
  - Total records deleted: X
```

**Failure Log Format:**
```
❌ Retention policy failed: [error message]
```

### Metrics to Track

| Metric | Expected Value | Alert Threshold |
|--------|---------------|-----------------|
| **Weekly purge success rate** | 100% | < 95% |
| **Average purge duration** | < 5 minutes | > 10 minutes |
| **AuditLog records purged/week** | ~100-500 | > 1000 (warning) |
| **Account/Client purges/week** | 0-10 | > 50 (warning) |

---

## Troubleshooting

### Common Issues

#### Issue 1: CRON Job Not Running

**Symptoms:**
- No logs in `/app/logs/retention_policy.log`
- Last modified time > 1 week old

**Diagnosis:**
```bash
# Check if CRON daemon is running
docker exec freelansign_cron_prod ps aux | grep crond

# Check CRON schedule
docker exec freelansign_cron_prod crontab -l
```

**Solution:**
```bash
# Restart CRON container
docker-compose -f docker-compose.prod.yml restart cron

# Verify logs reappear next Sunday 3am
```

---

#### Issue 2: Database Connection Errors

**Symptoms:**
```
❌ Retention policy failed: could not translate host name "postgres" to address
```

**Diagnosis:**
```bash
# Check database connectivity from CRON container
docker exec freelansign_cron_prod python manage.py check
```

**Solution:**
```bash
# Ensure postgres service is running
docker-compose -f docker-compose.prod.yml ps postgres

# Restart CRON container (re-establish network)
docker-compose -f docker-compose.prod.yml restart cron
```

---

#### Issue 3: Policy Disabled Error

**Symptoms:**
```
❌ RETENTION_POLICY_ENABLED is False.
```

**Diagnosis:**
```bash
# Check environment variable
docker exec freelansign_cron_prod env | grep RETENTION_POLICY_ENABLED
```

**Solution:**
```bash
# Update docker-compose.prod.yml
nano docker-compose.prod.yml

# Ensure:
# environment:
#   - RETENTION_POLICY_ENABLED=True

# Restart CRON container
docker-compose -f docker-compose.prod.yml up -d cron
```

---

#### Issue 4: High Purge Count Alert

**Symptoms:**
- Sentry warning: "High purge count: 1500 total records deleted"

**Diagnosis:**
```bash
# Check breakdown in Sentry alert
# - AuditLog: X records
# - Accounts: Y records
# - Clients: Z records
```

**Action:**
1. If expected (after initial deployment or data migration): Acknowledge alert, document reason
2. If unexpected: Investigate why so many old records accumulated, check for data retention issues

---

#### Issue 5: Transaction Rollback

**Symptoms:**
```
❌ Retention policy failed: TransactionManagementError
```

**Diagnosis:**
- Check Sentry for full stacktrace
- Review database logs for conflicts

**Solution:**
- Retry manually: `docker exec freelansign_backend_prod python manage.py apply_retention_policy`
- If persists: Contact DBA, check for long-running transactions

---

### Manual Execution

For immediate purge (outside CRON schedule):

```bash
# Production (dry-run first!)
docker exec freelansign_backend_prod python manage.py apply_retention_policy --dry-run
docker exec freelansign_backend_prod python manage.py apply_retention_policy

# Development (force required)
python manage.py apply_retention_policy --dry-run --force
python manage.py apply_retention_policy --force
```

---

## Rollback Strategy

### If Issues Arise During/After Deployment

#### 1. Immediate Mitigation

**Disable CRON** (stop automatic purge):

```bash
# Stop CRON container
docker-compose -f docker-compose.prod.yml stop cron

# Verify stopped
docker ps | grep freelansign_cron_prod  # Should return nothing
```

#### 2. Investigate Issue

- Review Sentry alerts
- Check `/app/logs/retention_policy.log`
- Verify database integrity

#### 3. Data Recovery (if accidental purge)

**CRITICAL**: Only possible if database backups exist.

```bash
# Restore from backup (before purge)
# Coordinate with DBA/DevOps team
pg_restore -U fs_user -d freelansign backup_2025-12-XX.sql
```

#### 4. Code Rollback (if command is buggy)

```bash
# Revert to previous backend image
docker-compose -f docker-compose.prod.yml down
docker pull ghcr.io/freelansign/freelansign-backend:previous-version
docker-compose -f docker-compose.prod.yml up -d
```

---

## Best Practices

### Pre-Deployment Checklist

- [ ] Run dry-run in staging environment
- [ ] Verify Sentry DSN is configured
- [ ] Ensure database backups are enabled (daily)
- [ ] Document expected purge counts (baseline)
- [ ] Notify team of deployment (Sunday 3am first execution)
- [ ] Schedule manual check Monday morning (after first run)

### Post-Deployment Checklist

- [ ] Verify CRON container is running
- [ ] Check first purge logs (Sunday 3am)
- [ ] Verify Sentry received success/failure alerts
- [ ] Review purge counts match expectations
- [ ] Update team on results

### Monthly Review

- [ ] Review purge counts trend (increasing/decreasing?)
- [ ] Check for Sentry alerts (any failures?)
- [ ] Verify log file rotation (not growing indefinitely)
- [ ] Validate compliance with GDPR (no data > retention period)

---

## Command Reference

### Management Command

**File**: `/backend/apps/core/management/commands/apply_retention_policy.py`

**Usage**:
```bash
python manage.py apply_retention_policy [--dry-run] [--force]
```

**Flags**:
- `--dry-run`: Simulate purge without making database changes (shows what would be deleted)
- `--force`: Override `RETENTION_POLICY_ENABLED=False` (dev environment only)

**Examples**:
```bash
# Production dry-run
python manage.py apply_retention_policy --dry-run

# Production live purge
python manage.py apply_retention_policy

# Development (force required)
python manage.py apply_retention_policy --force --dry-run
```

---

## Security Considerations

### Access Control

- **CRON Container**: Read-only access to backend code, write access to `/app/logs`
- **Database**: Full access (required for hard delete)
- **Environment Variables**: Sensitive (SECRET_KEY, DATABASE_PASSWORD) - secure storage required

### Audit Trail

- All purge operations logged to `/app/logs/retention_policy.log`
- Sentry tracks all executions (success/failure)
- Database transactions ensure atomicity (all-or-nothing)

### Data Protection

- **Protection Rules**: Accounts/Clients with active or recent quotes are NOT purged
- **Transaction Rollback**: Any error during purge triggers full rollback (no partial delete)
- **Dry-Run Mode**: Test before production purge

---

## FAQ

**Q: Can I change retention periods after deployment?**
A: Yes, update environment variables and restart CRON container. Changes take effect next Sunday 3am.

**Q: What happens if CRON execution fails?**
A: Sentry alert triggers immediately. Next week's execution will retry (catchup purge).

**Q: Can I run purge manually outside CRON schedule?**
A: Yes, use `docker exec freelansign_backend_prod python manage.py apply_retention_policy` (dry-run first!).

**Q: How do I verify data was purged?**
A: Check logs, Sentry summary, or query database (see "Post-Deployment Validation" section).

**Q: What if I accidentally purge production data?**
A: Restore from database backup (coordinate with DBA). This is why dry-run is CRITICAL.

---

## Contact

**Issues**: https://github.com/FreelanSign/FreelanSign/issues/72
**Team**: @Bertrand2808
**Documentation**: `/docs/deployment/retention-policy.md`

---

**Last Updated**: 2025-12-12
**Author**: @Bertrand2808
**Validated By**: [Pending DPO/Legal Review]
