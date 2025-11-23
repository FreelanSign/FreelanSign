# Monitoring & Alerting Guide

Comprehensive monitoring setup using Sentry (errors), UptimeRobot/BetterStack (uptime), and log management.

## Overview

**Monitoring Stack**:
- **Sentry**: Django error tracking & performance monitoring
- **UptimeRobot** or **BetterStack**: HTTP/HTTPS uptime monitoring
- **Log Rotation**: Automated log management (7/4/1 retention)
- **Docker Stats**: Resource usage monitoring

## 1. Sentry (Error Tracking)

### Setup (Already Configured)

Sentry is already integrated in `backend/config/settings.py:371-382`.

### Get Sentry DSN

1. Go to [Sentry.io](https://sentry.io)
2. Create account (free tier: 5,000 events/month)
3. Create new project:
   - Platform: **Django**
   - Project name: **FreelanSign Production**
4. Copy DSN from Settings → Client Keys (DSN)

### Configure in .env

```env
SENTRY_DSN=https://abc123def456@o123456.ingest.sentry.io/789012
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

### Verify Installation

```bash
# SSH to VPS
ssh deploy@your-server-ip

# Test Sentry integration
docker compose -f docker-compose.prod.yml exec backend python manage.py shell
```

In shell:
```python
from sentry_sdk import capture_message
capture_message("Test from production - monitoring is working!")
```

Check Sentry dashboard within 1-2 minutes for the test message.

### Sentry Features

**Error Tracking**:
- Automatic Django error capture
- Stack traces with context
- User identification
- Breadcrumbs (logs before error)

**Performance Monitoring**:
- API endpoint performance
- Database query performance
- Slow transaction alerts

**Releases**:
Track errors by deployment version:

```bash
# Set release in .env
SENTRY_RELEASE=v0.3.0
```

In settings.py (add to Sentry init):
```python
sentry_sdk.init(
    dsn=SENTRY_DSN,
    environment=env("SENTRY_ENVIRONMENT", default="production"),
    release=env("SENTRY_RELEASE", default=None),
    # ... other config
)
```

### Sentry Alerts

Configure in Sentry dashboard:

1. **Alerts → Create Alert**
2. **Alert conditions**:
   - Issue is first seen: Immediate notification
   - Issue frequency above threshold: 10 events in 1 hour
   - Error rate increases: 25% change
3. **Actions**:
   - Email notification
   - Slack integration
   - PagerDuty (for critical)

### Sentry Best Practices

```python
# Tag errors for better filtering
import sentry_sdk

sentry_sdk.set_tag("feature", "quote_generation")
sentry_sdk.set_tag("user_type", "freelancer")

# Add context
sentry_sdk.set_context("quote", {
    "id": quote_id,
    "status": quote.status,
})

# Capture specific exceptions
try:
    risky_operation()
except SpecificError as e:
    sentry_sdk.capture_exception(e)
```

---

## 2. UptimeRobot (Uptime Monitoring)

### Setup

1. **Sign up**: [UptimeRobot.com](https://uptimerobot.com) (free tier: 50 monitors)
2. **Add New Monitor**:
   - Monitor Type: **HTTP(s)**
   - Friendly Name: **FreelanSign Production**
   - URL: `https://your-domain.com`
   - Monitoring Interval: **5 minutes** (free tier)

3. **Advanced Settings**:
   - HTTP Method: **GET**
   - Timeout: **30 seconds**
   - SSL Check: **Enabled**

4. **Configure Alerts**:
   - Email: your-email@domain.com
   - SMS (optional, paid)
   - Slack/Discord webhook

### Additional Monitors

**API Health Check**:
```
Monitor Type: HTTP(s)
URL: https://your-domain.com/api/
Expected Keyword: "detail" or "message"
Interval: 5 minutes
```

**Admin Panel**:
```
Monitor Type: HTTP(s)
URL: https://your-domain.com/admin/
Expected Status: 200 or 302 (redirect)
Interval: 10 minutes
```

**SSL Certificate**:
```
Monitor Type: HTTP(s)
URL: https://your-domain.com
SSL Expiry: Alert 14 days before expiry
```

### Status Page (Public)

Create public status page:
1. UptimeRobot → Status Pages → Add Status Page
2. Select monitors to display
3. Custom domain: `status.your-domain.com`
4. Share URL with users

---

## 3. BetterStack (Alternative to UptimeRobot)

### Why BetterStack?

- Better UI/UX
- Incident management
- More detailed analytics
- Better alerting (phone calls)
- Free tier: 10 monitors, 3,000 heartbeats/month

### Setup

1. **Sign up**: [BetterStack.com/uptime](https://betterstack.com/uptime)
2. **Create Monitor**:
   - Type: **HTTP**
   - Name: **FreelanSign Production**
   - URL: `https://your-domain.com`
   - Check frequency: **60 seconds** (free tier)
   - Regions: Select multiple (US, EU, Asia)

3. **Expected Response**:
   - Status code: **200**
   - Response time: < 2000ms
   - SSL valid

4. **On-Call Schedule**:
   - Add team members
   - Escalation policy
   - Phone call alerts (paid)

### Heartbeat Monitoring

For cron jobs and backups:

1. Create **Heartbeat Monitor** in BetterStack
2. Get heartbeat URL: `https://uptime.betterstack.com/api/v1/heartbeat/xyz`

3. Add to cron job:
```bash
0 3 * * * /home/deploy/FreelanSign/scripts/backup.sh && curl -m 10 https://uptime.betterstack.com/api/v1/heartbeat/xyz
```

If backup fails or doesn't run, BetterStack alerts you.

### Integrations

- **Slack**: Real-time alerts in channel
- **Discord**: Webhook notifications
- **PagerDuty**: For critical alerts
- **Email**: Multiple recipients

---

## 4. Log Management

### Log Rotation (Already Configured)

Log rotation is configured in `logrotate.conf` (7 daily, 4 weekly, 1 monthly).

### View Logs

**Application logs**:
```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Backend only
docker compose -f docker-compose.prod.yml logs -f backend

# Last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100 backend

# Since 1 hour ago
docker compose -f docker-compose.prod.yml logs --since=1h backend
```

**Nginx access logs**:
```bash
# Via Docker volume
docker exec freelansign_frontend_prod tail -f /var/log/nginx/access.log

# Via host (if mounted)
tail -f /var/lib/docker/volumes/freelansign_nginx_logs_prod/_data/access.log
```

**Nginx error logs**:
```bash
docker exec freelansign_frontend_prod tail -f /var/log/nginx/error.log
```

**Django application logs**:
```bash
# Via Docker volume
docker exec freelansign_backend_prod tail -f /app/logs/app.log

# Via host (if mounted)
tail -f /var/lib/docker/volumes/freelansign_backend_logs_prod/_data/app.log
```

### Log Analysis

**Search for errors**:
```bash
docker compose -f docker-compose.prod.yml logs | grep -i error
docker compose -f docker-compose.prod.yml logs | grep -i exception
docker compose -f docker-compose.prod.yml logs | grep -E "5[0-9]{2}"
```

**Monitor specific endpoint**:
```bash
docker exec freelansign_frontend_prod tail -f /var/log/nginx/access.log | grep "/api/quotes"
```

**Count errors by type**:
```bash
docker compose -f docker-compose.prod.yml logs backend | grep ERROR | awk '{print $6}' | sort | uniq -c | sort -rn
```

### Centralized Logging (Optional)

For production, consider centralized logging:

**Option 1: Loki + Grafana** (self-hosted):
```yaml
# docker-compose.logging.yml
services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - loki_data:/loki

  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log
      - /var/lib/docker/containers:/var/lib/docker/containers

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
```

**Option 2: Papertrail** (SaaS):
- Free tier: 50MB/month, 7-day retention
- Simple rsyslog integration

**Option 3: Logtail** (BetterStack):
- Integrated with BetterStack
- SQL queries on logs
- 1GB/month free tier

---

## 5. Resource Monitoring

### Docker Stats

Real-time container resource usage:

```bash
# One-time snapshot
docker stats --no-stream

# Continuous monitoring
docker stats

# Specific containers
docker stats freelansign_backend_prod freelansign_postgres_prod
```

### Resource Alerts

Create monitoring script `scripts/monitor-resources.sh`:

```bash
#!/bin/bash
THRESHOLD_CPU=80
THRESHOLD_MEM=90

# Get container stats
STATS=$(docker stats --no-stream --format "{{.Name}}: CPU={{.CPUPerc}} MEM={{.MemPerc}}")

echo "$STATS" | while read -r line; do
    CONTAINER=$(echo "$line" | cut -d: -f1)
    CPU=$(echo "$line" | grep -oP 'CPU=\K[0-9.]+')
    MEM=$(echo "$line" | grep -oP 'MEM=\K[0-9.]+')

    if (( $(echo "$CPU > $THRESHOLD_CPU" | bc -l) )); then
        echo "ALERT: $CONTAINER CPU usage high: ${CPU}%"
        # Send alert (email, Slack, etc.)
    fi

    if (( $(echo "$MEM > $THRESHOLD_MEM" | bc -l) )); then
        echo "ALERT: $CONTAINER Memory usage high: ${MEM}%"
        # Send alert
    fi
done
```

Schedule in cron:
```cron
*/5 * * * * /home/deploy/FreelanSign/scripts/monitor-resources.sh
```

### System Monitoring

**Disk space**:
```bash
df -h
docker system df
```

**Memory**:
```bash
free -h
```

**Swap usage**:
```bash
swapon --show
```

**Network**:
```bash
# Connection count
ss -s

# Active connections
ss -tunap
```

---

## 6. Application Health Endpoint

Create health check endpoint for monitoring.

**Backend**: `apps/core/views/health.py`
```python
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        return JsonResponse({
            "status": "healthy",
            "database": "connected",
        })
    except Exception as e:
        return JsonResponse({
            "status": "unhealthy",
            "error": str(e),
        }, status=503)
```

**URL**: `config/urls.py`
```python
from apps.core.views.health import health_check

urlpatterns = [
    path('health/', health_check, name='health'),
    # ... other urls
]
```

**Monitor this endpoint**:
- UptimeRobot: `https://your-domain.com/api/health/`
- Expected keyword: `"healthy"`
- Alert if: keyword missing or status ≠ 200

---

## 7. Alert Channels

### Email Alerts

Configure for all monitoring tools:
- Sentry errors
- UptimeRobot downtime
- Backup failures
- Resource alerts

**Test email alerts**:
```bash
# Test UptimeRobot alert
curl -X POST https://api.uptimerobot.com/v2/newMonitor \
  -d api_key=your_key \
  -d type=1 \
  -d url=https://your-domain.com \
  -d alert_contacts=email@example.com
```

### Slack Integration

1. **Create Slack App**:
   - Go to [api.slack.com/apps](https://api.slack.com/apps)
   - Create New App
   - Add Incoming Webhooks

2. **Get Webhook URL**:
   ```
   https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
   ```

3. **Configure in monitoring tools**:
   - **Sentry**: Integrations → Slack
   - **UptimeRobot**: Alert Contacts → Webhook → Slack format
   - **BetterStack**: Integrations → Slack

4. **Test Slack webhook**:
```bash
curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"🚨 Test alert from FreelanSign monitoring"}'
```

### Discord Integration

Similar to Slack, use webhook URL:
```
https://discord.com/api/webhooks/123456789/abcdefghijklmnop
```

---

## 8. Monitoring Dashboard

### Quick Status Check Script

Create `scripts/status.sh`:

```bash
#!/bin/bash
echo "=== FreelanSign Production Status ==="
echo ""
echo "Services:"
docker compose -f /home/deploy/FreelanSign/docker-compose.prod.yml ps
echo ""
echo "Resources:"
docker stats --no-stream
echo ""
echo "Disk Usage:"
df -h /
echo ""
echo "Backup Status:"
ls -lh /home/deploy/backups/daily/ | tail -3
echo ""
echo "Recent Errors:"
docker compose -f /home/deploy/FreelanSign/docker-compose.prod.yml logs --tail=50 | grep -i error | tail -5
```

Usage:
```bash
chmod +x scripts/status.sh
./scripts/status.sh
```

---

## Monitoring Checklist

### Initial Setup
- [ ] Sentry DSN configured in .env
- [ ] Sentry test message sent successfully
- [ ] UptimeRobot or BetterStack account created
- [ ] Main website monitor configured
- [ ] API health endpoint monitor configured
- [ ] SSL certificate monitoring enabled
- [ ] Alert email addresses verified
- [ ] Slack/Discord webhooks configured (optional)

### Daily/Weekly Checks
- [ ] Check Sentry dashboard for new errors
- [ ] Review UptimeRobot uptime percentage (should be >99.5%)
- [ ] Verify backups are running (check logs)
- [ ] Monitor disk space usage
- [ ] Review Docker resource usage

### Monthly Tasks
- [ ] Review Sentry error trends
- [ ] Test alert notifications
- [ ] Verify backup restore process
- [ ] Check log rotation working
- [ ] Review monitoring costs (stay within free tiers)

---

## Monitoring Costs

### Free Tier Limits

**Sentry**:
- 5,000 errors/month
- 10,000 performance transactions/month
- 1 project
- **Cost if exceeded**: $26/month for 50k errors

**UptimeRobot**:
- 50 monitors
- 5-minute intervals
- Email alerts
- **Cost if exceeded**: $7/month for 1-minute intervals

**BetterStack**:
- 10 monitors
- 60-second intervals
- 3,000 heartbeats/month
- **Cost if exceeded**: $18/month for 30-second intervals

**Total monthly cost (free tiers)**: **$0**
**Total monthly cost (paid, if needed)**: ~$51/month

---

## Troubleshooting

### Sentry not receiving errors

```bash
# Check DSN configured
docker compose -f docker-compose.prod.yml exec backend env | grep SENTRY

# Test connection
docker compose -f docker-compose.prod.yml exec backend python -c "
import sentry_sdk
from django.conf import settings
print(f'DSN: {settings.SENTRY_DSN}')
sentry_sdk.capture_message('Manual test')
"

# Check Sentry logs
docker compose -f docker-compose.prod.yml logs backend | grep -i sentry
```

### UptimeRobot false positives

- Increase timeout to 60 seconds
- Check from multiple regions
- Verify firewall not blocking UptimeRobot IPs

### High resource usage alerts

```bash
# Identify heavy process
docker stats --no-stream

# Check logs for errors
docker compose -f docker-compose.prod.yml logs --tail=100

# Restart heavy service
docker compose -f docker-compose.prod.yml restart backend
```

---

## Resources

- [Sentry Django Documentation](https://docs.sentry.io/platforms/python/guides/django/)
- [UptimeRobot API Documentation](https://uptimerobot.com/api/)
- [BetterStack Documentation](https://betterstack.com/docs)
- [Docker Logging Best Practices](https://docs.docker.com/config/containers/logging/)
