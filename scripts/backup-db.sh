#!/bin/bash
################################################################################
# Database Backup Script
# Purpose: Create a backup of the PostgreSQL database
# Usage: ./scripts/backup-db.sh [backup_name]
#
# Features:
# - Creates timestamped backups
# - Compresses backups with gzip
# - Supports custom backup names
# - Retention policy (keeps last 30 days by default)
################################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_ROOT/backups"

# Configuration
RETENTION_DAYS=30
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
CUSTOM_NAME="${1:-}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}CodeRenew Database Backup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if DATABASE_URL is set
if [ -z "${DATABASE_URL:-}" ]; then
    echo -e "${RED}Error: DATABASE_URL environment variable is not set${NC}"
    echo -e "${YELLOW}Please set DATABASE_URL in your .env file or export it:${NC}"
    echo "  export DATABASE_URL=postgresql://user:password@localhost:5432/dbname"
    exit 1
fi

# Parse DATABASE_URL to extract connection details
# Format: postgresql://user:password@host:port/dbname
if [[ $DATABASE_URL =~ postgresql://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+) ]]; then
    DB_USER="${BASH_REMATCH[1]}"
    DB_PASSWORD="${BASH_REMATCH[2]}"
    DB_HOST="${BASH_REMATCH[3]}"
    DB_PORT="${BASH_REMATCH[4]}"
    DB_NAME="${BASH_REMATCH[5]}"
else
    echo -e "${RED}Error: Could not parse DATABASE_URL${NC}"
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Generate backup filename
if [ -n "$CUSTOM_NAME" ]; then
    BACKUP_FILE="$BACKUP_DIR/${CUSTOM_NAME}_${TIMESTAMP}.sql.gz"
else
    BACKUP_FILE="$BACKUP_DIR/coderenew_backup_${TIMESTAMP}.sql.gz"
fi

echo -e "${YELLOW}Database: ${DB_NAME}${NC}"
echo -e "${YELLOW}Host: ${DB_HOST}:${DB_PORT}${NC}"
echo -e "${YELLOW}Backup file: ${BACKUP_FILE}${NC}"
echo ""

# Create backup
echo -e "${YELLOW}Creating backup...${NC}"

export PGPASSWORD="$DB_PASSWORD"

pg_dump \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --username="$DB_USER" \
    --dbname="$DB_NAME" \
    --format=plain \
    --no-owner \
    --no-acl \
    --verbose \
    2>&1 | gzip > "$BACKUP_FILE"

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo ""
    echo -e "${GREEN}✓ Backup created successfully${NC}"
    echo -e "${GREEN}  File: ${BACKUP_FILE}${NC}"
    echo -e "${GREEN}  Size: ${BACKUP_SIZE}${NC}"
else
    echo ""
    echo -e "${RED}✗ Backup failed${NC}"
    exit 1
fi

# Clean up old backups
echo ""
echo -e "${YELLOW}Cleaning up old backups (keeping last ${RETENTION_DAYS} days)...${NC}"

find "$BACKUP_DIR" -name "*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete

OLD_BACKUP_COUNT=$(find "$BACKUP_DIR" -name "*.sql.gz" -type f | wc -l | tr -d ' ')
echo -e "${GREEN}✓ Cleanup complete (${OLD_BACKUP_COUNT} backups remaining)${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Backup complete!${NC}"
echo -e "${GREEN}========================================${NC}"

unset PGPASSWORD
