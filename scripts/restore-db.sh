#!/bin/bash
################################################################################
# Database Restore Script
# Purpose: Restore PostgreSQL database from a backup
# Usage: ./scripts/restore-db.sh <backup_file>
#
# WARNING: This will DROP and recreate the database!
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

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}CodeRenew Database Restore${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if backup file is provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No backup file specified${NC}"
    echo ""
    echo "Usage: $0 <backup_file>"
    echo ""
    echo "Available backups:"
    ls -lh "$BACKUP_DIR"/*.sql.gz 2>/dev/null || echo "  No backups found"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Error: Backup file not found: ${BACKUP_FILE}${NC}"
    exit 1
fi

# Check if DATABASE_URL is set
if [ -z "${DATABASE_URL:-}" ]; then
    echo -e "${RED}Error: DATABASE_URL environment variable is not set${NC}"
    echo -e "${YELLOW}Please set DATABASE_URL in your .env file or export it:${NC}"
    echo "  export DATABASE_URL=postgresql://user:password@localhost:5432/dbname"
    exit 1
fi

# Parse DATABASE_URL to extract connection details
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

BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)

echo -e "${YELLOW}Database: ${DB_NAME}${NC}"
echo -e "${YELLOW}Host: ${DB_HOST}:${DB_PORT}${NC}"
echo -e "${YELLOW}Backup file: ${BACKUP_FILE}${NC}"
echo -e "${YELLOW}Backup size: ${BACKUP_SIZE}${NC}"
echo ""

# Confirmation prompt
echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║                       ⚠️  WARNING ⚠️                        ║${NC}"
echo -e "${RED}║                                                            ║${NC}"
echo -e "${RED}║  This operation will DROP the existing database and       ║${NC}"
echo -e "${RED}║  restore it from the backup file. ALL CURRENT DATA        ║${NC}"
echo -e "${RED}║  WILL BE PERMANENTLY LOST!                                ║${NC}"
echo -e "${RED}║                                                            ║${NC}"
echo -e "${RED}║  Database: ${DB_NAME}                                      ║${NC}"
echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

read -p "Type 'RESTORE' to confirm: " confirm

if [ "$confirm" != "RESTORE" ]; then
    echo -e "${YELLOW}Restore cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}Starting database restore...${NC}"

export PGPASSWORD="$DB_PASSWORD"

# Drop existing database (if exists) and recreate
echo -e "${YELLOW}1. Dropping existing database...${NC}"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;" || true

echo -e "${YELLOW}2. Creating fresh database...${NC}"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME;"

# Restore from backup
echo -e "${YELLOW}3. Restoring data from backup...${NC}"
gunzip -c "$BACKUP_FILE" | psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"

if [ ${PIPESTATUS[1]} -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Database restored successfully${NC}"
else
    echo ""
    echo -e "${RED}✗ Restore failed${NC}"
    exit 1
fi

# Run migrations to ensure schema is up to date
echo ""
echo -e "${YELLOW}4. Running migrations to ensure schema is current...${NC}"
cd "$PROJECT_ROOT/backend"
alembic upgrade head

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Restore complete!${NC}"
echo -e "${GREEN}========================================${NC}"

unset PGPASSWORD
