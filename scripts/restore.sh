#!/bin/bash
#
# FreelanSign Database Restore Script
# Restores PostgreSQL database from backup file
#
# Refactored to handle container name based on environment (prod/dev).
# @author Bertrand2808
# @version 1.0
# @date 2025-11-23
set -e
set -o pipefail

# Configuration
# Configuration
BACKUP_DIR="/home/deploy/backups"
DB_NAME="${DATABASE_NAME:-freelansign}"
DB_USER="${DATABASE_USER:-fs_user}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

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

# Usage information
usage() {
    echo "Usage: $0 <backup_file> docker <env>"
    echo "  env: dev or prod"
    echo ""
    echo "Examples:"
    echo "  $0 /home/deploy/backups/daily/backup_20250121_143022.sql.gz docker prod"
    echo "  $0 latest docker dev  # Restores the most recent daily backup to dev"
    echo ""
    echo "Available backups:"
    echo ""
    echo "Daily backups:"
    ls -lht "$BACKUP_DIR/daily/" | head -5 | tail -4
    echo ""
    echo "Weekly backups:"
    ls -lht "$BACKUP_DIR/weekly/" | head -5 | tail -4
    echo ""
    echo "Monthly backups:"
    ls -lht "$BACKUP_DIR/monthly/" | head -5 | tail -4
    exit 1
}

# Check arguments
# Check arguments
if [ $# -lt 3 ]; then
    error "Insufficient arguments"
    usage
fi

BACKUP_FILE="$1"
MODE="$2"
ENV="$3"

if [ "$MODE" != "docker" ]; then
    error "Second argument must be 'docker'"
    usage
fi

if [ "$ENV" == "prod" ]; then
    DB_CONTAINER="freelansign_postgres_prod"
    COMPOSE_FILE="docker-compose.prod.yml"
elif [ "$ENV" == "dev" ]; then
    DB_CONTAINER="freelansign_postgres"
    COMPOSE_FILE="docker-compose.yml"
else
    error "Environment must be 'dev' or 'prod'"
    usage
fi

# Handle 'latest' keyword
if [ "$BACKUP_FILE" == "latest" ]; then
    BACKUP_FILE=$(ls -t "$BACKUP_DIR/daily/"backup_*.sql.gz 2>/dev/null | head -1)
    if [ -z "$BACKUP_FILE" ]; then
        error "No backups found in $BACKUP_DIR/daily/"
        exit 1
    fi
    log "Using latest backup: $BACKUP_FILE"
fi

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    error "Backup file not found: $BACKUP_FILE"
    usage
fi

# Check if Docker container is running
if ! docker ps | grep -q "$DB_CONTAINER"; then
    error "Database container $DB_CONTAINER is not running"
    exit 1
fi

# Confirmation prompt
echo ""
warn "⚠️  WARNING: This will REPLACE the current database with the backup!"
echo ""
echo "Database: $DB_NAME"
echo "Backup file: $BACKUP_FILE"
echo "Backup size: $(du -h "$BACKUP_FILE" | cut -f1)"
echo "Backup date: $(stat -c %y "$BACKUP_FILE" 2>/dev/null || stat -f "%Sm" "$BACKUP_FILE")"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    log "Restore cancelled by user"
    exit 0
fi

# Create a safety backup before restore
SAFETY_BACKUP="/tmp/pre_restore_backup_$(date +%Y%m%d_%H%M%S).sql.gz"
log "Creating safety backup before restore: $SAFETY_BACKUP"
docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" | gzip > "$SAFETY_BACKUP"
log "Safety backup created: $(du -h "$SAFETY_BACKUP" | cut -f1)"

# Stop application (to prevent connections during restore)
log "Stopping application containers..."
docker compose -f "$COMPOSE_FILE" stop backend frontend

# Wait for connections to close
sleep 3

# Terminate existing connections
log "Terminating existing database connections..."
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d postgres -c \
    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();" \
    >/dev/null 2>&1 || true

# Drop and recreate database
log "Dropping existing database..."
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"

log "Creating fresh database..."
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# Restore from backup
# Restore from backup
log "Restoring from backup..."

# Determine if file is gzipped based on extension
if [[ "$BACKUP_FILE" == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" | docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME"
else
    cat "$BACKUP_FILE" | docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME"
fi

if [ $? -eq 0 ]; then
    log "✅ Database restored successfully"
else
    error "❌ Restore failed!"
    warn "You can restore the safety backup from: $SAFETY_BACKUP"
    exit 1
fi

# Restart application
log "Restarting application containers..."
docker compose -f "$COMPOSE_FILE" start backend frontend

# Wait for services to be ready
sleep 5

# Verify database
log "Verifying database..."
TABLES=$(docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")

if [ "$TABLES" -gt 0 ]; then
    log "✅ Database verification successful ($TABLES tables found)"
else
    error "❌ Database verification failed (no tables found)"
    exit 1
fi

# Cleanup safety backup (optional)
echo ""
read -p "Delete safety backup at $SAFETY_BACKUP? (yes/no): " DELETE_SAFETY

if [ "$DELETE_SAFETY" == "yes" ]; then
    rm "$SAFETY_BACKUP"
    log "Safety backup deleted"
else
    log "Safety backup kept at: $SAFETY_BACKUP"
fi

log "✅ Restore completed successfully"
exit 0
