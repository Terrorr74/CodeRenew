#!/bin/bash

# EPSS Integration - Staging Deployment Script
# Automates the staging deployment process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STAGING_HOST="${STAGING_HOST:-staging.coderenew.com}"
STAGING_USER="${STAGING_USER:-deploy}"
PROJECT_DIR="/var/www/coderenew"
BACKUP_DIR="$HOME/backups"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

confirm() {
    read -p "$(echo -e ${YELLOW}$1${NC}) [y/N] " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

# Header
echo "╔═══════════════════════════════════════════════╗"
echo "║  EPSS Integration - Staging Deployment        ║"
echo "║  CodeRenew                                     ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# Pre-flight checks
log_info "Running pre-flight checks..."

# Check SSH connectivity
if ! ssh -q -o BatchMode=yes -o ConnectTimeout=5 "$STAGING_USER@$STAGING_HOST" exit; then
    log_error "Cannot connect to staging server: $STAGING_HOST"
    log_info "Please check your SSH configuration"
    exit 1
fi
log_success "SSH connection verified"

# Check git status
if [[ -n $(git status --porcelain) ]]; then
    log_warning "You have uncommitted changes"
    if ! confirm "Continue anyway?"; then
        exit 0
    fi
fi

# Confirm deployment
echo ""
log_info "Deployment Details:"
echo "  Server: $STAGING_HOST"
echo "  User: $STAGING_USER"
echo "  Project: $PROJECT_DIR"
echo ""

if ! confirm "Proceed with deployment?"; then
    log_info "Deployment cancelled"
    exit 0
fi

echo ""
log_info "Starting deployment..."

# Step 1: Create Backup
log_info "Step 1/9: Creating backup..."

ssh "$STAGING_USER@$STAGING_HOST" << 'ENDSSH'
    set -e

    # Create backup directory
    mkdir -p $HOME/backups

    # Backup database
    echo "  → Backing up database..."
    sudo -u postgres pg_dump coderenew_staging > \
        $HOME/backups/coderenew_staging_pre_epss_$(date +%Y%m%d_%H%M%S).sql

    # Backup code
    echo "  → Backing up code..."
    cd /var/www/coderenew
    sudo tar -czf $HOME/backups/coderenew_code_$(date +%Y%m%d_%H%M%S).tar.gz .

    ls -lh $HOME/backups/ | tail -2
ENDSSH

log_success "Backup completed"

# Step 2: Pull Latest Code
log_info "Step 2/9: Pulling latest code..."

ssh "$STAGING_USER@$STAGING_HOST" << 'ENDSSH'
    set -e
    cd /var/www/coderenew

    # Stash local changes
    git stash || true

    # Pull latest
    git pull origin main

    # Verify EPSS files
    if [ ! -f "backend/app/services/epss/epss_service.py" ]; then
        echo "ERROR: EPSS service file not found!"
        exit 1
    fi

    echo "  → EPSS files verified"
ENDSSH

log_success "Code updated"

# Step 3: Install Backend Dependencies
log_info "Step 3/9: Installing backend dependencies..."

ssh "$STAGING_USER@$STAGING_HOST" << 'ENDSSH'
    set -e
    cd /var/www/coderenew/backend

    # Activate virtualenv
    source venv/bin/activate

    # Install dependencies
    pip install -r requirements.txt --quiet

    # Verify httpx installed
    if ! pip list | grep -q httpx; then
        echo "ERROR: httpx not installed!"
        exit 1
    fi

    echo "  → Dependencies installed"
ENDSSH

log_success "Backend dependencies installed"

# Step 4: Run Database Migration
log_info "Step 4/9: Running database migration..."

ssh "$STAGING_USER@$STAGING_HOST" << 'ENDSSH'
    set -e
    cd /var/www/coderenew/backend

    source venv/bin/activate

    # Check current version
    echo "  → Current migration: $(alembic current)"

    # Run migration
    alembic upgrade head

    # Verify new columns exist
    if ! psql coderenew_staging -c "\d scan_results" | grep -q epss_score; then
        echo "ERROR: EPSS columns not found!"
        exit 1
    fi

    echo "  → Migration completed: $(alembic current)"
ENDSSH

log_success "Database migration completed"

# Step 5: Restart Backend API
log_info "Step 5/9: Restarting backend API..."

ssh "$STAGING_USER@$STAGING_HOST" << 'ENDSSH'
    set -e

    # Restart API service
    sudo systemctl restart coderenew-api

    # Wait for service to start
    sleep 3

    # Check service status
    if ! sudo systemctl is-active --quiet coderenew-api; then
        echo "ERROR: API service failed to start!"
        sudo systemctl status coderenew-api
        exit 1
    fi

    echo "  → API service running"
ENDSSH

log_success "Backend API restarted"

# Step 6: Restart Celery Services
log_info "Step 6/9: Restarting Celery services..."

ssh "$STAGING_USER@$STAGING_HOST" << 'ENDSSH'
    set -e

    # Restart Celery worker
    sudo systemctl restart celery-worker

    # Restart Celery beat
    sudo systemctl restart celery-beat

    # Wait for services to start
    sleep 2

    # Check service status
    if ! sudo systemctl is-active --quiet celery-worker; then
        echo "ERROR: Celery worker failed to start!"
        exit 1
    fi

    if ! sudo systemctl is-active --quiet celery-beat; then
        echo "ERROR: Celery beat failed to start!"
        exit 1
    fi

    echo "  → Celery services running"
ENDSSH

log_success "Celery services restarted"

# Step 7: Deploy Frontend
log_info "Step 7/9: Deploying frontend..."

ssh "$STAGING_USER@$STAGING_HOST" << 'ENDSSH'
    set -e
    cd /var/www/coderenew/frontend

    # Install dependencies if needed
    npm install --quiet

    # Build frontend
    npm run build

    # Restart frontend service
    pm2 restart coderenew-frontend || sudo systemctl restart coderenew-frontend

    echo "  → Frontend deployed"
ENDSSH

log_success "Frontend deployed"

# Step 8: Verification Tests
log_info "Step 8/9: Running verification tests..."

# Test API health
if curl -f -s "http://$STAGING_HOST/api/health" > /dev/null; then
    log_success "  → API health check passed"
else
    log_error "  → API health check failed!"
fi

# Test EPSS service
ssh "$STAGING_USER@$STAGING_HOST" << 'ENDSSH'
    set -e
    cd /var/www/coderenew/backend
    source venv/bin/activate

    # Quick Python test
    python3 << 'PYEND'
import asyncio
from app.services.epss import get_epss_service

async def test():
    epss = get_epss_service()
    score = await epss.get_epss_score('CVE-2021-44228')
    if score:
        print(f"  → EPSS service test passed (score: {score.epss_score:.4f})")
        return True
    else:
        print("  → EPSS service test failed!")
        return False

result = asyncio.run(test())
exit(0 if result else 1)
PYEND

ENDSSH

if [ $? -eq 0 ]; then
    log_success "  → EPSS service test passed"
else
    log_error "  → EPSS service test failed!"
fi

# Check database
ssh "$STAGING_USER@$STAGING_HOST" << 'ENDSSH'
    # Verify EPSS columns exist
    if psql coderenew_staging -c "SELECT cve_id, epss_score FROM scan_results LIMIT 1" > /dev/null 2>&1; then
        echo "  → Database schema verified"
    else
        echo "  → Database schema verification failed!"
        exit 1
    fi
ENDSSH

log_success "Verification tests completed"

# Step 9: Post-Deployment Summary
log_info "Step 9/9: Generating deployment summary..."

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║  Deployment Summary                            ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

ssh "$STAGING_USER@$STAGING_HOST" << 'ENDSSH'
    echo "📊 Service Status:"
    echo "  API:          $(systemctl is-active coderenew-api)"
    echo "  Celery Worker: $(systemctl is-active celery-worker)"
    echo "  Celery Beat:   $(systemctl is-active celery-beat)"
    echo ""

    echo "📦 Database:"
    echo "  Migration:    $(cd /var/www/coderenew/backend && source venv/bin/activate && alembic current 2>/dev/null | head -1)"
    echo ""

    echo "🔗 URLs:"
    echo "  Frontend:     http://staging.coderenew.com"
    echo "  API:          http://staging.coderenew.com/api"
    echo "  Health:       http://staging.coderenew.com/api/health"
    echo ""

    echo "📝 Logs:"
    echo "  API:          /var/log/coderenew/api.log"
    echo "  Celery:       /var/log/celery/worker.log"
    echo ""
ENDSSH

log_success "Deployment completed successfully! 🎉"

echo ""
echo "📋 Next Steps:"
echo "  1. Monitor logs for 24 hours"
echo "  2. Test EPSS feature in browser: http://$STAGING_HOST/scans/1"
echo "  3. Verify Celery tasks are running"
echo "  4. Run performance tests"
echo ""
echo "📖 Full deployment guide: EPSS_STAGING_DEPLOYMENT.md"
echo ""

# Optional: Open browser
if command -v open &> /dev/null; then
    if confirm "Open staging URL in browser?"; then
        open "http://$STAGING_HOST"
    fi
fi

echo ""
log_info "Deployment complete at $(date)"
