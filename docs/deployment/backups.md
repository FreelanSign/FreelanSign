# Backup & Restore Guide

Automated PostgreSQL backup system with 7/4/1 retention policy and offsite storage.

## Retention Policy

- **Daily**: 7 backups (last 7 days)
- **Weekly**: 4 backups (last 4 weeks, created every Sunday)
- **Monthly**: 1 backup (last month, created on 1st of month)

**Total local storage**: ~12 backups at any time (varies by database size)

## Setup

### 1. Install Backup Script

```bash
# On VPS
cd /home/deploy/FreelanSign

# Make scripts executable
chmod +x scripts/backup.sh scripts/restore.sh

# Create backup directory
mkdir -p /home/deploy/backups/{daily,weekly,monthly}
```

### 2. Test Manual Backup

```bash
cd /home/deploy/FreelanSign
./scripts/backup.sh
```

Expected output:
```
[2025-01-21 14:30:22] Starting backup process...
[2025-01-21 14:30:23] Creating daily backup: /home/deploy/backups/daily/backup_20250121_143022.sql.gz
[2025-01-21 14:30:25] Daily backup created successfully (2.3M)
[2025-01-21 14:30:25] Cleaning up old backups...
[2025-01-21 14:30:25] Backup summary:
  Daily backups:   1 files (2.3M)
  Weekly backups:  0 files (0)
  Monthly backups: 0 files (0)
  Total size: 2.3M
[2025-01-21 14:30:25] Backup process completed successfully
```

### 3. Schedule Automated Backups

```bash
# Edit crontab
crontab -e
```

Add daily backup at 3 AM:
```cron
# FreelanSign daily backup at 3 AM
0 3 * * * /home/deploy/FreelanSign/scripts/backup.sh >> /var/log/freelansign-backup.log 2>&1
```

Alternative schedules:
```cron
# Every 6 hours
0 */6 * * * /home/deploy/FreelanSign/scripts/backup.sh >> /var/log/freelansign-backup.log 2>&1

# Every 12 hours
0 */12 * * * /home/deploy/FreelanSign/scripts/backup.sh >> /var/log/freelansign-backup.log 2>&1

# Twice daily (3 AM and 3 PM)
0 3,15 * * * /home/deploy/FreelanSign/scripts/backup.sh >> /var/log/freelansign-backup.log 2>&1
```

### 4. Verify Cron Job

```bash
# List cron jobs
crontab -l

# Check logs after scheduled time
tail -f /var/log/freelansign-backup.log
```

## Offsite Backup (Scaleway Object Storage)

### Setup S3-Compatible Storage

1. **Create Scaleway Object Storage bucket**:
   - Go to [Scaleway Console](https://console.scaleway.com/object-storage/buckets)
   - Create bucket: `freelansign-backups`
   - Region: Choose closest to VPS
   - Visibility: Private

2. **Generate API keys**:
   - IAM → API Keys → Generate API Key
   - Note: Access Key ID, Secret Key

3. **Install AWS CLI**:
```bash
# On VPS
apt install -y awscli

# Configure AWS CLI for Scaleway
aws configure
```

Enter:
```
AWS Access Key ID: your_scaleway_access_key
AWS Secret Access Key: your_scaleway_secret_key
Default region name: fr-par  # or your region
Default output format: json
```

4. **Set environment variables**:
```bash
# Add to ~/.bashrc or /etc/environment
export S3_BUCKET="freelansign-backups"
export S3_ENDPOINT="https://s3.fr-par.scw.cloud"
export S3_REGION="fr-par"
```

Apply:
```bash
source ~/.bashrc
```

5. **Test S3 upload**:
```bash
aws s3 ls --endpoint-url=$S3_ENDPOINT
aws s3 cp /tmp/test.txt s3://$S3_BUCKET/test/ --endpoint-url=$S3_ENDPOINT
```

6. **Run backup with offsite**:
```bash
./scripts/backup.sh
```

Should now show:
```
[2025-01-21 14:30:26] Uploading to Scaleway Object Storage...
[2025-01-21 14:30:28] Offsite backup uploaded successfully
```

### Offsite Storage Costs

**Scaleway Object Storage Pricing** (as of 2025):
- Storage: €0.01/GB/month
- Egress: Free within Scaleway region

**Example monthly cost**:
- Database: 100MB
- Daily backups: 7 × 100MB = 700MB
- Weekly backups: 4 × 100MB = 400MB
- Monthly: 1 × 100MB = 100MB
- **Total**: ~1.2GB = **€0.012/month (~1 cent)**

## Restore from Backup

### List Available Backups

```bash
cd /home/deploy/FreelanSign

# List all backups
ls -lh backups/daily/
ls -lh backups/weekly/
ls -lh backups/monthly/
```

### Restore from Local Backup

**Restore latest backup**:
```bash
./scripts/restore.sh latest
```

**Restore specific backup**:
```bash
./scripts/restore.sh /home/deploy/backups/daily/backup_20250121_143022.sql.gz
```

**Restore weekly backup**:
```bash
./scripts/restore.sh /home/deploy/backups/weekly/backup_week_20250119.sql.gz
```

The script will:
1. Show backup details and ask for confirmation
2. Create safety backup before restore
3. Stop application containers
4. Drop and recreate database
5. Restore from backup file
6. Restart application containers
7. Verify restoration

### Restore from Offsite Backup

1. **List offsite backups**:
```bash
aws s3 ls s3://$S3_BUCKET/backups/daily/ --endpoint-url=$S3_ENDPOINT
```

2. **Download backup**:
```bash
aws s3 cp s3://$S3_BUCKET/backups/daily/backup_20250121_143022.sql.gz \
    /tmp/restore.sql.gz \
    --endpoint-url=$S3_ENDPOINT
```

3. **Restore**:
```bash
./scripts/restore.sh /tmp/restore.sql.gz
```

### Manual Restore (Without Script)

```bash
# Stop application
docker compose -f docker-compose.prod.yml stop backend frontend

# Restore database
gunzip -c /path/to/backup.sql.gz | \
    docker exec -i freelansign_postgres_prod \
    psql -U fs_user -d freelansign

# Restart application
docker compose -f docker-compose.prod.yml start backend frontend
```

## Monitoring Backups

### Check Backup Status

```bash
# View backup summary
ls -lh /home/deploy/backups/*/ | grep backup_

# Check total backup size
du -sh /home/deploy/backups

# Count backups by type
echo "Daily: $(ls /home/deploy/backups/daily/ | wc -l)"
echo "Weekly: $(ls /home/deploy/backups/weekly/ | wc -l)"
echo "Monthly: $(ls /home/deploy/backups/monthly/ | wc -l)"
```

### Monitor Cron Logs

```bash
# View recent backup logs
tail -50 /var/log/freelansign-backup.log

# Follow logs in real-time
tail -f /var/log/freelansign-backup.log

# Check for errors
grep ERROR /var/log/freelansign-backup.log
```

### Verify Backup Integrity

Test restore to verify backup is valid:

```bash
# Create test database
docker exec freelansign_postgres_prod \
    psql -U fs_user -d postgres -c "CREATE DATABASE test_restore;"

# Test restore
gunzip -c /home/deploy/backups/daily/backup_latest.sql.gz | \
    docker exec -i freelansign_postgres_prod \
    psql -U fs_user -d test_restore

# Check tables
docker exec freelansign_postgres_prod \
    psql -U fs_user -d test_restore -c "\dt"

# Cleanup
docker exec freelansign_postgres_prod \
    psql -U fs_user -d postgres -c "DROP DATABASE test_restore;"
```

## Disaster Recovery

### Complete System Failure

1. **Provision new VPS** (see VPS Setup Guide)

2. **Install Docker and application** (see Build & Deploy)

3. **Download latest backup from offsite**:
```bash
aws s3 cp s3://$S3_BUCKET/backups/daily/ /tmp/restore/ \
    --endpoint-url=$S3_ENDPOINT --recursive

# Get latest backup
LATEST_BACKUP=$(ls -t /tmp/restore/backup_*.sql.gz | head -1)
```

4. **Restore database**:
```bash
cd /home/deploy/FreelanSign
./scripts/restore.sh $LATEST_BACKUP
```

5. **Verify application**:
```bash
curl -I https://your-domain.com
docker compose -f docker-compose.prod.yml logs -f
```

### Data Corruption

If database is corrupted but VPS is intact:

1. **Stop application immediately**:
```bash
docker compose -f docker-compose.prod.yml stop backend
```

2. **Create corruption backup** (for investigation):
```bash
docker exec freelansign_postgres_prod \
    pg_dump -U fs_user -d freelansign | \
    gzip > /tmp/corrupted_$(date +%Y%m%d_%H%M%S).sql.gz
```

3. **Restore from latest good backup**:
```bash
./scripts/restore.sh latest
```

### Accidental Data Deletion

Restore from backup taken before deletion:

```bash
# List backups to find one before deletion
ls -lht /home/deploy/backups/daily/

# Restore specific backup
./scripts/restore.sh /home/deploy/backups/daily/backup_20250120_030000.sql.gz
```

## Backup Best Practices

1. **Test restores monthly**: Verify backups can actually be restored
2. **Monitor backup size**: Sudden changes may indicate issues
3. **Keep offsite backups**: Protects against hardware failure
4. **Document recovery time**: Know how long full restore takes
5. **Automate monitoring**: Set up alerts if backups fail
6. **Secure backups**: Encrypt sensitive data, restrict access
7. **Version control**: Keep application code in git for full recovery

## Troubleshooting

### Backup script fails

```bash
# Check Docker container running
docker ps | grep postgres

# Check disk space
df -h

# Check permissions
ls -l /home/deploy/backups/

# Run manually with verbose output
bash -x ./scripts/backup.sh
```

### Backup too large / slow

```bash
# Check database size
docker exec freelansign_postgres_prod \
    psql -U fs_user -d freelansign -c \
    "SELECT pg_size_pretty(pg_database_size('freelansign'));"

# Optimize database (run during low traffic)
docker exec freelansign_postgres_prod \
    psql -U fs_user -d freelansign -c "VACUUM FULL ANALYZE;"
```

### Restore fails

```bash
# Check backup file integrity
gunzip -t /path/to/backup.sql.gz

# Check database container
docker logs freelansign_postgres_prod

# Verify database user exists
docker exec freelansign_postgres_prod \
    psql -U postgres -c "\du"
```

### Offsite upload fails

```bash
# Test S3 connection
aws s3 ls --endpoint-url=$S3_ENDPOINT

# Check credentials
aws configure list

# Test upload
echo "test" > /tmp/test.txt
aws s3 cp /tmp/test.txt s3://$S3_BUCKET/test.txt --endpoint-url=$S3_ENDPOINT
```

### Cron job not running

```bash
# Check cron service
systemctl status cron

# Check cron logs
grep CRON /var/log/syslog

# Test cron manually
/home/deploy/FreelanSign/scripts/backup.sh
```

## Backup Automation Checklist

- [ ] Backup script installed and executable
- [ ] Backup directories created
- [ ] Manual backup tested successfully
- [ ] Cron job scheduled
- [ ] Cron job verified in logs
- [ ] Offsite storage configured (optional)
- [ ] Offsite backup tested
- [ ] Restore script tested
- [ ] Monthly restore drill scheduled
- [ ] Monitoring/alerts configured
- [ ] Documentation accessible to team
- [ ] Recovery time objective (RTO) documented

## Resources

- [PostgreSQL Backup Documentation](https://www.postgresql.org/docs/current/backup.html)
- [Scaleway Object Storage](https://www.scaleway.com/en/docs/storage/object/)
- [AWS CLI S3 Commands](https://docs.aws.amazon.com/cli/latest/reference/s3/)
