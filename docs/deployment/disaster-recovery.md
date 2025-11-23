# Disaster Recovery Runbook

## Overview

This runbook provides step-by-step procedures for recovering from various disaster scenarios. All procedures assume you have access to:
- VPS via SSH
- Backup files (local or Scaleway Object Storage)
- Docker registry credentials
- `.env` file backup

**Recovery Time Objectives (RTO):**
- Complete server rebuild: 2-4 hours
- Database restoration: 15-30 minutes
- Application deployment: 10-15 minutes

**Recovery Point Objectives (RPO):**
- Database: 24 hours (daily backups)
- Code: Real-time (Git repository)
- Media files: 24 hours (daily backups)

## Disaster Scenarios

### 1. Database Corruption/Loss

**Detection:**
- Application errors connecting to database
- Data inconsistencies
- PostgreSQL container won't start

**Recovery Procedure:**

```bash
# 1. Stop application (prevent further writes)
cd /opt/freelansign
docker compose stop backend

# 2. Verify backup availability
ls -lh /var/backups/freelansign/
# Or from Scaleway Object Storage
s3cmd ls s3://freelansign-backups/

# 3. Stop PostgreSQL
docker compose stop postgres

# 4. Remove corrupted database volume (if needed)
docker volume rm freelansign_postgres_data
# Or backup existing data first:
docker volume create postgres_data_backup
docker run --rm -v freelansign_postgres_data:/from -v postgres_data_backup:/to alpine sh -c "cp -av /from/. /to"

# 5. Restore from backup
./scripts/restore.sh /var/backups/freelansign/backup-YYYY-MM-DD.sql.gz

# 6. Verify database integrity
docker compose exec postgres psql -U $DATABASE_USER -d $DATABASE_NAME -c "\dt"
docker compose exec postgres psql -U $DATABASE_USER -d $DATABASE_NAME -c "SELECT COUNT(*) FROM auth_user;"

# 7. Restart application
docker compose up -d

# 8. Verify health
curl https://yourdomain.com/api/health/
```

**Validation:**
- Health check passes
- Users can login
- Data appears current (check recent records)
- No errors in logs

---

### 2. Complete Server Loss

**Scenario:** VPS destroyed, needs full rebuild

**Recovery Procedure:**

```bash
# === Phase 1: Provision New VPS ===

# 1. Create new Scaleway VPS-START-S instance
# Note IP address: __.___.___.___

# 2. SSH into new server
ssh root@NEW_VPS_IP

# 3. Create swap file
dd if=/dev/zero of=/swapfile bs=1G count=2
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# 4. Update system
apt update && apt upgrade -y

# 5. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install -y docker-compose-plugin

# 6. Install required packages
apt install -y git curl wget certbot python3-certbot-nginx s3cmd

# === Phase 2: Configure Server ===

# 7. Create app directory
mkdir -p /opt/freelansign
cd /opt/freelansign

# 8. Clone repository (if using Git deployment) or prepare for image pull
# Option A: Git clone
git clone https://github.com/your-org/freelansign.git .

# Option B: Just setup docker-compose
wget https://raw.githubusercontent.com/your-org/freelansign/main/docker-compose.prod.yml

# 9. Restore .env file (from backup or secrets manager)
vim .env
# Paste production environment variables

# 10. Update DNS A record to point to NEW_VPS_IP
# (via DNS provider dashboard)

# === Phase 3: Restore Data ===

# 11. Download backups from Scaleway Object Storage
s3cmd --configure  # Enter Scaleway credentials
s3cmd get s3://freelansign-backups/backup-latest.sql.gz /tmp/

# 12. Restore media files
s3cmd get --recursive s3://freelansign-backups/media/ /opt/freelansign/media/

# === Phase 4: Deploy Application ===

# 13. Login to Docker registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# 14. Pull images
docker compose -f docker-compose.prod.yml pull

# 15. Start database first
docker compose -f docker-compose.prod.yml up -d postgres
sleep 10

# 16. Restore database
gunzip < /tmp/backup-latest.sql.gz | docker compose exec -T postgres psql -U $DATABASE_USER -d $DATABASE_NAME

# 17. Start all services
docker compose -f docker-compose.prod.yml up -d

# === Phase 5: Configure SSL ===

# 18. Obtain SSL certificate (DNS must be pointing to new IP)
certbot --nginx -d yourdomain.com -d www.yourdomain.com --non-interactive --agree-tos -m admin@yourdomain.com

# 19. Test auto-renewal
certbot renew --dry-run

# === Phase 6: Verify ===

# 20. Check all services running
docker compose ps

# 21. Test health endpoint
curl https://yourdomain.com/api/health/

# 22. Test application login
# Open browser: https://yourdomain.com

# 23. Configure monitoring
# - Update UptimeRobot/BetterStack with new IP
# - Verify Sentry receiving events

# 24. Setup backup cron
crontab -e
# Add: 0 2 * * * /opt/freelansign/scripts/backup.sh
```

**Estimated Time:** 2-4 hours

**Validation:**
- All containers running
- SSL certificate valid
- Health check passes
- Users can access application
- Recent data present
- Monitoring active

---

### 3. Application Container Crash Loop

**Detection:**
- Container constantly restarting
- 502/503 errors from Nginx
- `docker compose ps` shows "Restarting"

**Recovery Procedure:**

```bash
# 1. Check container logs
docker compose logs backend --tail=100

# 2. Identify error type:

# === Case A: Configuration Error ===
# Fix .env file or settings, then:
docker compose restart backend

# === Case B: Database Migration Issue ===
# Roll back migrations
docker compose exec backend python manage.py migrate catalog 0012  # rollback to specific
docker compose restart backend

# === Case C: Corrupted Code/Image ===
# Re-pull image
docker compose pull backend
docker compose up -d backend

# === Case D: Resource Exhaustion ===
# Check memory
free -h
docker stats

# Kill memory hogs or restart containers
docker compose restart

# If OOM, increase swap:
dd if=/dev/zero of=/swapfile2 bs=1G count=2
chmod 600 /swapfile2
mkswap /swapfile2
swapon /swapfile2

# 3. Monitor recovery
docker compose logs -f backend
```

---

### 4. Database Connection Pool Exhausted

**Detection:**
- "Too many connections" errors
- Slow API responses
- Database refusing connections

**Recovery Procedure:**

```bash
# 1. Check current connections
docker compose exec postgres psql -U $DATABASE_USER -d $DATABASE_NAME -c "SELECT count(*) FROM pg_stat_activity;"

# 2. Identify long-running queries
docker compose exec postgres psql -U $DATABASE_USER -d $DATABASE_NAME -c "
SELECT pid, now() - query_start as duration, query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC
LIMIT 10;"

# 3. Kill problematic connections (if safe)
docker compose exec postgres psql -U $DATABASE_USER -d $DATABASE_NAME -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid != pg_backend_pid() AND state = 'idle' AND now() - state_change > interval '5 minutes';"

# 4. Restart application (clears connection pool)
docker compose restart backend

# 5. If persistent, increase max_connections temporarily
# Edit postgres.conf:
docker compose exec postgres psql -U postgres -c "ALTER SYSTEM SET max_connections = 100;"
docker compose restart postgres

# 6. Monitor for recurrence
watch -n 5 "docker compose exec postgres psql -U $DATABASE_USER -d $DATABASE_NAME -c 'SELECT count(*) FROM pg_stat_activity;'"
```

---

### 5. Disk Space Exhaustion

**Detection:**
- "No space left on device" errors
- Containers failing to start
- `df -h` shows 100% usage

**Recovery Procedure:**

```bash
# 1. Check disk usage
df -h
du -sh /var/lib/docker/*

# 2. Clean Docker resources
docker system prune -a -f --volumes
# WARNING: Removes all unused images/volumes

# 3. Clean old backups
find /var/backups/freelansign/ -type f -mtime +30 -delete

# 4. Clean logs
truncate -s 0 /var/log/nginx/*.log
docker compose exec backend sh -c "truncate -s 0 logs/*.log"

# 5. Rotate logs immediately
logrotate -f /etc/logrotate.d/nginx

# 6. If still critical, move backups offsite only
s3cmd put /var/backups/freelansign/*.gz s3://freelansign-backups/
rm /var/backups/freelansign/*.gz

# 7. Restart services
docker compose restart

# 8. Monitor disk usage
watch -n 10 df -h
```

**Prevention:**
- Setup automated cleanup cron
- Monitor disk usage alerts (< 80%)
- Regular offsite backup transfer

---

### 6. SSL Certificate Expiry

**Detection:**
- Browser warnings about invalid certificate
- API clients failing with SSL errors
- Certbot renewal failed emails

**Recovery Procedure:**

```bash
# 1. Check certificate status
certbot certificates

# 2. Attempt renewal
certbot renew --force-renewal

# 3. If renewal fails, regenerate
certbot delete --cert-name yourdomain.com
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 4. Verify certificate
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# 5. Reload Nginx
docker compose restart nginx
# Or if Nginx is host-based:
systemctl reload nginx

# 6. Setup renewal monitoring
echo "0 0 1 * * certbot renew --quiet" >> /var/spool/cron/crontabs/root
```

---

### 7. Security Breach

**Detection:**
- Unauthorized access alerts
- Unusual activity in logs
- Sentry security warnings
- Compromised credentials reported

**Immediate Actions:**

```bash
# 1. ISOLATE - Block all traffic except SSH
ufw default deny incoming
ufw allow 22/tcp
ufw enable

# 2. ASSESS - Check for indicators of compromise
grep "Failed password" /var/log/auth.log | tail -50
docker compose logs backend | grep -E "403|401|500" | tail -100
docker compose exec postgres psql -U $DATABASE_USER -d $DATABASE_NAME -c "SELECT * FROM auth_user ORDER BY last_login DESC LIMIT 20;"

# 3. CONTAIN - Stop services
docker compose stop

# 4. INVESTIGATE - Preserve evidence
tar -czf /tmp/incident-$(date +%F).tar.gz /var/log/ /opt/freelansign/logs/
s3cmd put /tmp/incident-$(date +%F).tar.gz s3://freelansign-backups/incidents/

# 5. ERADICATE - Rotate all secrets
# Generate new SECRET_KEY, database passwords, API keys
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Update .env with new secrets
vim .env

# 6. RESTORE - Deploy clean images
docker compose pull
docker compose up -d

# 7. HARDEN - Update security
apt update && apt upgrade -y
docker compose exec backend python manage.py changepassword admin

# Force password reset for all users (if needed)
docker compose exec backend python manage.py shell -c "
from apps.user.models import User
User.objects.all().update(password='')
"

# 8. MONITOR - Watch for further activity
tail -f /var/log/auth.log &
docker compose logs -f backend &
```

**Post-Incident:**
- Conduct security audit
- Update access controls
- Review and patch vulnerabilities
- Document incident and lessons learned

---

## Backup Verification

**Monthly test restoration:**

```bash
# 1. Create test environment
mkdir -p /tmp/recovery-test
cd /tmp/recovery-test

# 2. Use docker-compose with test database
cat > docker-compose.test.yml <<EOF
services:
  postgres-test:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: test_db
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_pass
    ports:
      - "5433:5432"
EOF

# 3. Start test database
docker compose -f docker-compose.test.yml up -d

# 4. Restore latest backup
gunzip < /var/backups/freelansign/backup-latest.sql.gz | docker compose -f docker-compose.test.yml exec -T postgres-test psql -U test_user -d test_db

# 5. Verify data
docker compose -f docker-compose.test.yml exec postgres-test psql -U test_user -d test_db -c "SELECT COUNT(*) FROM auth_user;"

# 6. Cleanup
docker compose -f docker-compose.test.yml down -v
cd && rm -rf /tmp/recovery-test
```

---

## Emergency Contacts & Resources

**Infrastructure:**
- Scaleway Support: https://console.scaleway.com/support
- DNS Provider: [Your DNS provider contact]

**Services:**
- Brevo Support: support@brevo.com
- Sentry: support@sentry.io
- GitHub: support@github.com

**Internal:**
- On-call Engineer: [Phone/Email]
- Team Lead: [Phone/Email]
- Backup Location: s3://freelansign-backups/

**Documentation:**
- Repository: https://github.com/your-org/freelansign
- Deployment Guide: docs/deployment/vps-setup.md
- Environment Config: docs/deployment/environment-config.md

---

## Recovery Decision Matrix

| Scenario | Severity | RTO | Action |
|----------|----------|-----|--------|
| Database corruption | Critical | 30 min | Restore from backup |
| Server loss | Critical | 4 hours | Full rebuild |
| Container crash | High | 10 min | Restart/rollback |
| Connection pool exhausted | High | 15 min | Restart/tune |
| Disk full | High | 20 min | Clean resources |
| SSL expired | Medium | 15 min | Renew certificate |
| Security breach | Critical | Immediate | Isolate & investigate |

---

## Post-Recovery Checklist

After any disaster recovery:

- [ ] Document incident timeline
- [ ] Verify all services operational
- [ ] Check data integrity
- [ ] Update monitoring/alerts
- [ ] Review and improve runbook
- [ ] Conduct team debrief
- [ ] Update backup/recovery procedures
- [ ] Test similar scenarios in staging
