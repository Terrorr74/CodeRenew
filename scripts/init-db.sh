#!/bin/bash
################################################################################
# Database Initialization Script
# Purpose: Initialize database and run all migrations for a fresh deployment
# Usage: ./scripts/init-db.sh
################################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}CodeRenew Database Initialization${NC}"
echo -e "${GREEN}========================================${NC}"
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
echo ""

# Wait for database to be ready
echo -e "${YELLOW}Waiting for database to be ready...${NC}"
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if pg_isready -d "$DATABASE_URL" > /dev/null 2>&1; then
        echo -e "${GREEN}Database is ready!${NC}"
        break
    fi

    attempt=$((attempt + 1))
    echo "Attempt $attempt/$max_attempts: Database not ready, waiting..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}Error: Database did not become ready in time${NC}"
    exit 1
fi

echo ""

# Check current Alembic version
echo -e "${YELLOW}Checking current database version...${NC}"
if alembic current 2>/dev/null; then
    echo -e "${GREEN}Database is already initialized${NC}"
    echo ""
    echo -e "${YELLOW}Current migrations:${NC}"
    alembic current -v
else
    echo -e "${YELLOW}Database not initialized yet${NC}"
fi

echo ""

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
alembic upgrade head

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Migrations completed successfully${NC}"
else
    echo -e "${RED}✗ Migration failed${NC}"
    exit 1
fi

echo ""

# Show final state
echo -e "${YELLOW}Final database state:${NC}"
alembic current -v

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Database initialization complete!${NC}"
echo -e "${GREEN}========================================${NC}"
