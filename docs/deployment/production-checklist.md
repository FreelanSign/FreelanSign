# Production Deployment Checklist

## Pre-Deployment

### Environment Configuration
- [ ] `.env` file configured with production values
- [ ] `DEBUG=False` confirmed
- [ ] `SECRET_KEY` set to strong random value (50+ chars)
- [ ] `ALLOWED_HOSTS` configured with production domains
- [ ] Database credentials secured (strong password)
- [ ] Brevo SMTP credentials configured
- [ ] Sentry DSN configured for error tracking

### SSL/Security
- [ ] SSL certificate obtained via Certbot
- [ ] Certificate auto-renewal configured (`systemctl status certbot.timer`)
- [ ] Nginx configured for HTTPS redirect
- [ ] Security headers enabled in Nginx
- [ ] Django security settings verified:
  - `SECURE_SSL_REDIRECT=True`
  - `SECURE_HSTS_SECONDS=31536000`
  - `SESSION_COOKIE_SECURE=True`
  - `CSRF_COOKIE_SECURE=True`

### Infrastructure
- [ ] VPS provisioned (Scaleway VPS-START-S or equivalent)
- [ ] 2GB SWAP file created and active (`swapon -s`)
- [ ] DNS records configured (A record pointing to VPS IP)
- [ ] Docker + Docker Compose installed
- [ ] Firewall configured (ports 80, 443, 22 open)
- [ ] SSH key authentication enabled
- [ ] Root login disabled

### Database
- [ ] PostgreSQL tuned for 2GB RAM (postgres.conf)
- [ ] Database backups configured
- [ ] Connection pooling verified in Django settings
- [ ] Initial migrations run successfully

### Docker Images
- [ ] Backend image built and pushed to registry
- [ ] Frontend image built and pushed to registry
- [ ] Images tagged with version/commit hash
- [ ] Registry authentication configured on VPS

## Deployment Verification

### Health Checks
```bash
# Backend health endpoint
curl -f https://yourdomain.com/api/health/
# Expected: {"status":"healthy","checks":{"database":"ok"}}

# Frontend accessible
curl -f https://yourdomain.com/
# Expected: 200 OK

# API accessible
curl -f https://yourdomain.com/api/docs/
# Expected: Swagger UI loads
```

### Container Status
```bash
# All containers running
docker ps
# Expected: backend, frontend, postgres, nginx all "Up"

# Check container logs
docker compose logs backend --tail=50
docker compose logs frontend --tail=50
docker compose logs postgres --tail=50
```

### Resource Usage
```bash
# Memory usage
free -h
# Expected: < 80% usage, swap available

# Disk usage
df -h
# Expected: < 70% on root partition

# Docker disk usage
docker system df
# Expected: reasonable image/container sizes
```

### Database
```bash
# Connect to database
docker compose exec postgres psql -U $DATABASE_USER -d $DATABASE_NAME

# Check tables exist
\dt

# Check connection count
SELECT count(*) FROM pg_stat_activity;
# Expected: < max_connections (50)
```

### SSL Certificate
```bash
# Check certificate validity
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
# Expected: valid certificate chain, expiry > 30 days

# Test auto-renewal
sudo certbot renew --dry-run
# Expected: success
```

### Performance
```bash
# Response time check
time curl -o /dev/null -s -w '%{time_total}\n' https://yourdomain.com/api/health/
# Expected: < 0.5s

# Rate limiting test (should block after limit)
for i in {1..35}; do curl https://yourdomain.com/api/health/; done
# Expected: 429 after 30 requests
```

## Post-Deployment

### Monitoring
- [ ] UptimeRobot/BetterStack HTTP checks configured
- [ ] Sentry receiving error events (test with error)
- [ ] Log rotation active (`/var/log/nginx/`, backend logs)
- [ ] Backup cron job verified (`crontab -l`)

### Testing
- [ ] User registration flow works
- [ ] Login/logout works
- [ ] Password reset email sends (Brevo)
- [ ] File uploads work (media files)
- [ ] API endpoints respond correctly
- [ ] Frontend routing works (SPA navigation)

### Documentation
- [ ] `.env.example` updated with all required vars
- [ ] Deployment docs reflect current process
- [ ] Team notified of deployment
- [ ] Changelog updated (if applicable)

### Backup & Recovery
- [ ] Manual backup created post-deployment
- [ ] Backup restoration tested (on separate instance)
- [ ] Offsite backup uploaded to Scaleway Object Storage
- [ ] Recovery runbook verified

## Rollback Plan

If deployment fails:

1. **Quick rollback to previous version:**
```bash
# Pull previous image version
docker compose pull backend:previous-tag frontend:previous-tag

# Restart with previous version
docker compose up -d

# Verify health
curl https://yourdomain.com/api/health/
```

2. **Database rollback (if migrations applied):**
```bash
# Restore from latest backup
./scripts/restore.sh /path/to/backup.sql.gz
```

3. **Verify rollback:**
- Application accessible
- No errors in logs
- Health check passes

## Maintenance Tasks

### Weekly
- [ ] Check disk usage (`df -h`)
- [ ] Review error logs (Sentry dashboard)
- [ ] Verify backup success (check backup directory)
- [ ] Check SSL certificate expiry (`certbot certificates`)

### Monthly
- [ ] Update Docker images with security patches
- [ ] Review and prune old Docker images (`docker system prune`)
- [ ] Test backup restoration
- [ ] Review resource usage trends

### Quarterly
- [ ] Update dependencies (Django, React, Python packages)
- [ ] Review and update security settings
- [ ] Load testing
- [ ] Disaster recovery drill

## Troubleshooting

### Application not accessible
```bash
# Check Nginx status
sudo systemctl status nginx

# Check container status
docker compose ps

# Check logs
docker compose logs --tail=100
```

### Database connection errors
```bash
# Check PostgreSQL running
docker compose ps postgres

# Check connections
docker compose exec postgres psql -U $DATABASE_USER -c "SELECT count(*) FROM pg_stat_activity;"

# Check Django database settings
docker compose exec backend python manage.py dbshell
```

### High memory usage
```bash
# Check per-container usage
docker stats

# Check system memory
free -h

# Restart containers if needed
docker compose restart backend frontend
```

### SSL certificate issues
```bash
# Renew certificate manually
sudo certbot renew

# Check Nginx config
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

## Emergency Contacts

- **Hosting**: Scaleway Support
- **Domain**: DNS provider support
- **Email**: Brevo Support
- **Monitoring**: Sentry/UptimeRobot support
