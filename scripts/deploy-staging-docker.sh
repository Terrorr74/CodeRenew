#!/bin/bash

# EPSS Integration - Docker Staging Deployment Script
# Deploys CodeRenew to staging using Docker Compose

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILES="-f docker-compose.yml -f docker-compose.staging.yml"
ENV_FILE=".env.staging"

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

check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        log_error "Environment file $ENV_FILE not found!"
        log_info "Please create $ENV_FILE with required variables"
        log_info "Required: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, DATABASE_URL, REDIS_PASSWORD, SECRET_KEY"
        log_info "Optional: ANTHROPIC_API_KEY (for AI scanning), STRIPE_SECRET_KEY (for payments)"
        exit 1
    fi
    log_success "Environment file found"
}

# Header
echo "╔═══════════════════════════════════════════════╗"
echo "║  Docker Staging Deployment                    ║"
echo "║  EPSS Integration - CodeRenew                 ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# Pre-flight checks
log_info "Running pre-flight checks..."

# Check Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed"
    exit 1
fi
log_success "Docker is installed"

# Check Docker Compose
if ! docker compose version &> /dev/null; then
    log_error "Docker Compose is not installed"
    exit 1
fi
log_success "Docker Compose is installed"

# Check environment file
check_env_file

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
echo "  Environment: Staging"
echo "  Compose files: $COMPOSE_FILES"
echo "  Env file: $ENV_FILE"
echo ""

if ! confirm "Proceed with Docker deployment?"; then
    log_info "Deployment cancelled"
    exit 0
fi

echo ""
log_info "Starting Docker deployment..."

# Step 1: Create Backup
log_info "Step 1/8: Creating backup..."

if docker compose $COMPOSE_FILES ps | grep -q "coderenew_db_staging"; then
    BACKUP_DIR="./backups"
    mkdir -p "$BACKUP_DIR"

    BACKUP_FILE="$BACKUP_DIR/coderenew_staging_$(date +%Y%m%d_%H%M%S).sql"

    log_info "  → Backing up database to $BACKUP_FILE"
    docker compose $COMPOSE_FILES exec -T db pg_dump -U "${POSTGRES_USER:-postgres}" "${POSTGRES_DB:-coderenew_staging}" > "$BACKUP_FILE"

    gzip "$BACKUP_FILE"
    log_success "Backup completed: ${BACKUP_FILE}.gz"
else
    log_info "  → No existing database container, skipping backup"
fi

# Step 2: Pull Latest Code
log_info "Step 2/8: Pulling latest code..."
git pull origin main
log_success "Code updated"

# Step 3: Build Images
log_info "Step 3/8: Building Docker images..."
docker compose $COMPOSE_FILES build --no-cache
log_success "Images built"

# Step 4: Stop Existing Containers
log_info "Step 4/8: Stopping existing containers..."
docker compose $COMPOSE_FILES down --remove-orphans
log_success "Containers stopped"

# Step 5: Start Database and Redis
log_info "Step 5/8: Starting database and Redis..."
docker compose $COMPOSE_FILES up -d db redis

# Wait for database to be ready
log_info "  → Waiting for database to be ready..."
for i in {1..30}; do
    if docker compose $COMPOSE_FILES exec -T db pg_isready -U "${POSTGRES_USER:-postgres}" &> /dev/null; then
        log_success "Database is ready"
        break
    fi

    if [ $i -eq 30 ]; then
        log_error "Database failed to start"
        docker compose $COMPOSE_FILES logs db
        exit 1
    fi

    sleep 2
done

# Step 6: Run Database Migration
log_info "Step 6/8: Running database migration..."

docker compose $COMPOSE_FILES run --rm backend alembic current
log_info "  → Current migration version shown above"

docker compose $COMPOSE_FILES run --rm backend alembic upgrade head
log_success "Database migration completed"

# Verify EPSS columns exist
log_info "  → Verifying EPSS columns..."
if docker compose $COMPOSE_FILES exec -T db psql -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-coderenew_staging}" -c "\d scan_results" | grep -q "epss_score"; then
    log_success "EPSS columns verified"
else
    log_error "EPSS columns not found!"
    exit 1
fi

# Step 7: Start All Services
log_info "Step 7/8: Starting all services..."
docker compose $COMPOSE_FILES up -d

# Wait for services to be ready
log_info "  → Waiting for services to be ready..."
sleep 10

# Check service health
log_info "  → Checking service health..."
docker compose $COMPOSE_FILES ps

log_success "All services started"

# Step 8: Verification Tests
log_info "Step 8/8: Running verification tests..."

# Test API health
log_info "  → Testing API health endpoint..."
for i in {1..10}; do
    if docker compose $COMPOSE_FILES exec -T backend curl -f http://localhost:8000/api/v1/health &> /dev/null; then
        log_success "API health check passed"
        break
    fi

    if [ $i -eq 10 ]; then
        log_error "API health check failed!"
        docker compose $COMPOSE_FILES logs backend
        exit 1
    fi

    sleep 3
done

# Test EPSS service
log_info "  → Testing EPSS service..."
docker compose $COMPOSE_FILES exec -T backend python3 << 'PYEND'
import asyncio
from app.services.epss import get_epss_service

async def test():
    try:
        epss = get_epss_service()
        score = await epss.get_epss_score('CVE-2021-44228')
        if score and score.epss_score > 0:
            print(f"✅ EPSS service test passed (score: {score.epss_score:.4f})")
            return True
        else:
            print("❌ EPSS service test failed - no score returned")
            return False
    except Exception as e:
        print(f"❌ EPSS service test failed: {e}")
        return False

result = asyncio.run(test())
exit(0 if result else 1)
PYEND

if [ $? -eq 0 ]; then
    log_success "EPSS service test passed"
else
    log_error "EPSS service test failed!"
fi

# Check Celery workers
log_info "  → Checking Celery workers..."
if docker compose $COMPOSE_FILES exec -T celery_worker celery -A app.core.celery_app inspect ping &> /dev/null; then
    log_success "Celery workers are running"
else
    log_warning "Celery workers may not be responding"
fi

# Deployment Summary
echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║  Deployment Summary                            ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

echo "📊 Container Status:"
docker compose $COMPOSE_FILES ps --format "table {{.Service}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "📦 Database:"
DB_VERSION=$(docker compose $COMPOSE_FILES run --rm backend alembic current 2>/dev/null | head -1)
echo "  Migration:    $DB_VERSION"
echo ""

echo "🔗 Service URLs:"
echo "  Backend API:  http://localhost:8000"
echo "  Frontend:     http://localhost:3000"
echo "  API Health:   http://localhost:8000/api/v1/health"
echo "  Nginx:        http://localhost:8080"
echo ""

echo "📝 Useful Commands:"
echo "  View logs:     docker compose $COMPOSE_FILES logs -f [service]"
echo "  Stop all:      docker compose $COMPOSE_FILES down"
echo "  Restart:       docker compose $COMPOSE_FILES restart [service]"
echo "  Shell access:  docker compose $COMPOSE_FILES exec [service] /bin/bash"
echo ""

log_success "Docker deployment completed successfully! 🎉"

echo ""
echo "📋 Next Steps:"
echo "  1. Monitor logs: docker compose $COMPOSE_FILES logs -f"
echo "  2. Test EPSS feature in browser: http://localhost:3000/scans/1"
echo "  3. Verify Celery tasks: docker compose $COMPOSE_FILES exec celery_worker celery -A app.core.celery_app inspect active"
echo "  4. Check resource usage: docker stats"
echo ""

# Optional: Show live logs
if confirm "Show live logs?"; then
    docker compose $COMPOSE_FILES logs -f
fi

echo ""
log_info "Deployment complete at $(date)"
