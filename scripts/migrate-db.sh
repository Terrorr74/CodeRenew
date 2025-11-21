#!/bin/bash
################################################################################
# Database Migration Script
# Purpose: Run database migrations (upgrade or downgrade)
# Usage:
#   ./scripts/migrate-db.sh              # Upgrade to latest
#   ./scripts/migrate-db.sh upgrade      # Upgrade to latest
#   ./scripts/migrate-db.sh downgrade    # Downgrade one version
#   ./scripts/migrate-db.sh downgrade -1 # Downgrade one version
#   ./scripts/migrate-db.sh downgrade -2 # Downgrade two versions
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
BACKEND_DIR="$PROJECT_ROOT/backend"

# Parse arguments
ACTION="${1:-upgrade}"
TARGET="${2:-head}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}CodeRenew Database Migration${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if we're in the correct directory
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}Error: Backend directory not found at $BACKEND_DIR${NC}"
    exit 1
fi

cd "$BACKEND_DIR"

# Check if DATABASE_URL is set
if [ -z "${DATABASE_URL:-}" ]; then
    echo -e "${RED}Error: DATABASE_URL environment variable is not set${NC}"
    echo -e "${YELLOW}Please set DATABASE_URL in your .env file or export it:${NC}"
    echo "  export DATABASE_URL=postgresql://user:password@localhost:5432/dbname"
    exit 1
fi

echo -e "${YELLOW}Database URL: ${DATABASE_URL}${NC}"
echo -e "${YELLOW}Action: ${ACTION}${NC}"
echo ""

# Show current state
echo -e "${YELLOW}Current database version:${NC}"
alembic current -v
echo ""

# Confirm action if downgrading
if [ "$ACTION" == "downgrade" ]; then
    echo -e "${RED}WARNING: You are about to downgrade the database!${NC}"
    echo -e "${RED}This operation may result in data loss.${NC}"
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        echo -e "${YELLOW}Migration cancelled${NC}"
        exit 0
    fi
    echo ""
fi

# Run migration
echo -e "${YELLOW}Running migration: alembic ${ACTION} ${TARGET}${NC}"
echo ""

alembic "${ACTION}" "${TARGET}"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Migration completed successfully${NC}"
else
    echo ""
    echo -e "${RED}✗ Migration failed${NC}"
    exit 1
fi

echo ""

# Show final state
echo -e "${YELLOW}New database version:${NC}"
alembic current -v

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Migration complete!${NC}"
echo -e "${GREEN}========================================${NC}"
