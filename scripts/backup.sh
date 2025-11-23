#!/bin/bash
#
# FreelanSign Backup Script
# Backs up PostgreSQL database with 7/4/1 retention policy
# Daily: 7 days, Weekly: 4 weeks, Monthly: 1 month
#

set -e

# Configuration
BACKUP_DIR="/home/deploy/backups"
DB_CONTAINER="freelansign_postgres_prod"
DB_NAME="${DATABASE_NAME:-freelansign}"
DB_USER="${DATABASE_USER:-fs_user}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE=$(date +%Y%m%d)
DAY_OF_WEEK=$(date +%u)  # 1-7 (Monday=1, Sunday=7)
DAY_OF_MONTH=$(date +%d)

# Retention periods (in days)
DAILY_RETENTION=7
WEEKLY_RETENTION=28
MONTHLY_RETENTION=30

# Backup directories
DAILY_DIR="$BACKUP_DIR/daily"
WEEKLY_DIR="$BACKUP_DIR/weekly"
MONTHLY_DIR="$BACKUP_DIR/monthly"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create backup directories
mkdir -p "$DAILY_DIR" "$WEEKLY_DIR" "$MONTHLY_DIR"

# Log function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Check if Docker container is running
if ! docker ps | grep -q "$DB_CONTAINER"; then
    error "Database container $DB_CONTAINER is not running"
    exit 1
fi

log "Starting backup process..."

# Daily backup
DAILY_BACKUP="$DAILY_DIR/backup_${DATE}_${TIMESTAMP}.sql.gz"
log "Creating daily backup: $DAILY_BACKUP"

docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" | gzip > "$DAILY_BACKUP"

if [ $? -eq 0 ]; then
    log "Daily backup created successfully ($(du -h "$DAILY_BACKUP" | cut -f1))"
else
    error "Daily backup failed"
    exit 1
fi

# Weekly backup (every Sunday)
if [ "$DAY_OF_WEEK" -eq 7 ]; then
    WEEKLY_BACKUP="$WEEKLY_DIR/backup_week_${DATE}.sql.gz"
    log "Creating weekly backup: $WEEKLY_BACKUP"
    cp "$DAILY_BACKUP" "$WEEKLY_BACKUP"
    log "Weekly backup created ($(du -h "$WEEKLY_BACKUP" | cut -f1))"
fi

# Monthly backup (first day of month)
if [ "$DAY_OF_MONTH" -eq 01 ]; then
    MONTHLY_BACKUP="$MONTHLY_DIR/backup_month_${DATE}.sql.gz"
    log "Creating monthly backup: $MONTHLY_BACKUP"
    cp "$DAILY_BACKUP" "$MONTHLY_BACKUP"
    log "Monthly backup created ($(du -h "$MONTHLY_BACKUP" | cut -f1))"
fi

# Cleanup old backups
log "Cleaning up old backups..."

# Remove daily backups older than 7 days
REMOVED_DAILY=$(find "$DAILY_DIR" -name "backup_*.sql.gz" -mtime +$DAILY_RETENTION -delete -print | wc -l)
if [ "$REMOVED_DAILY" -gt 0 ]; then
    log "Removed $REMOVED_DAILY old daily backup(s)"
fi

# Remove weekly backups older than 28 days
REMOVED_WEEKLY=$(find "$WEEKLY_DIR" -name "backup_*.sql.gz" -mtime +$WEEKLY_RETENTION -delete -print | wc -l)
if [ "$REMOVED_WEEKLY" -gt 0 ]; then
    log "Removed $REMOVED_WEEKLY old weekly backup(s)"
fi

# Remove monthly backups older than 30 days
REMOVED_MONTHLY=$(find "$MONTHLY_DIR" -name "backup_*.sql.gz" -mtime +$MONTHLY_RETENTION -delete -print | wc -l)
if [ "$REMOVED_MONTHLY" -gt 0 ]; then
    log "Removed $REMOVED_MONTHLY old monthly backup(s)"
fi

# Display backup summary
log "Backup summary:"
echo "  Daily backups:   $(ls -1 "$DAILY_DIR" | wc -l) files ($(du -sh "$DAILY_DIR" | cut -f1))"
echo "  Weekly backups:  $(ls -1 "$WEEKLY_DIR" | wc -l) files ($(du -sh "$WEEKLY_DIR" | cut -f1))"
echo "  Monthly backups: $(ls -1 "$MONTHLY_DIR" | wc -l) files ($(du -sh "$MONTHLY_DIR" | cut -f1))"
echo "  Total size: $(du -sh "$BACKUP_DIR" | cut -f1)"

# Offsite backup to Scaleway Object Storage (optional)
if [ -n "$S3_BUCKET" ] && command -v aws &> /dev/null; then
    log "Uploading to Scaleway Object Storage..."

    # Upload daily backup
    aws s3 cp "$DAILY_BACKUP" "s3://$S3_BUCKET/backups/daily/" \
        --endpoint-url="$S3_ENDPOINT" \
        --region="$S3_REGION"

    if [ $? -eq 0 ]; then
        log "Offsite backup uploaded successfully"
    else
        warn "Offsite backup upload failed"
    fi

    # Cleanup old offsite backups
    if [ "$DAY_OF_WEEK" -eq 7 ]; then
        log "Cleaning up old offsite backups..."
        CUTOFF_DATE=$(date -d "-${DAILY_RETENTION} days" +%Y%m%d)
        aws s3 ls "s3://$S3_BUCKET/backups/daily/" --endpoint-url="$S3_ENDPOINT" | \
        while read -r line; do
            BACKUP_DATE=$(echo "$line" | grep -oP 'backup_\K\d{8}')
            if [ -n "$BACKUP_DATE" ] && [ "$BACKUP_DATE" -lt "$CUTOFF_DATE" ]; then
                BACKUP_FILE=$(echo "$line" | awk '{print $4}')
                aws s3 rm "s3://$S3_BUCKET/backups/daily/$BACKUP_FILE" \
                    --endpoint-url="$S3_ENDPOINT"
                log "Removed old offsite backup: $BACKUP_FILE"
            fi
        done
    fi
else
    warn "Offsite backup skipped (S3_BUCKET not configured or aws-cli not installed)"
fi

log "Backup process completed successfully"
exit 0
