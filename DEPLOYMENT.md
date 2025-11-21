# CodeRenew Deployment Guide

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Infrastructure Architecture](#infrastructure-architecture)
- [Local Development Setup](#local-development-setup)
- [Staging Deployment](#staging-deployment)
- [Production Deployment](#production-deployment)
- [Database Management](#database-management)
- [Monitoring and Logging](#monitoring-and-logging)
- [Troubleshooting](#troubleshooting)
- [Rollback Procedures](#rollback-procedures)

## Overview

CodeRenew is a WordPress compatibility scanner SaaS application built with:
- **Backend**: FastAPI (Python 3.11+), PostgreSQL, SQLAlchemy
- **Frontend**: Next.js 14+ (TypeScript), React
- **Infrastructure**: Docker, Docker Compose, Nginx, Redis
- **CI/CD**: GitHub Actions

This guide covers deployment to staging and production environments.

## Prerequisites

### System Requirements
- Docker 20.10+ and Docker Compose 2.0+
- PostgreSQL 15+ (or Docker image)
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- 2GB+ RAM minimum, 4GB+ recommended
- 20GB+ disk space

### Required Accounts & Keys
1. **Anthropic Claude API** - Get key from https://console.anthropic.com/
2. **Stripe** - Payment processing (https://dashboard.stripe.com/)
3. **Resend** - Email service (https://resend.com/)
4. **Domain & SSL** - Valid domain with SSL certificates

### Access Requirements
- SSH access to deployment server
- GitHub repository access
- Docker registry access (GitHub Container Registry)

## Infrastructure Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                    ┌────▼─────┐
                    │  Nginx   │  (Port 80/443)
                    │  Reverse │  - SSL Termination
                    │  Proxy   │  - Rate Limiting
                    └─┬──────┬─┘  - Load Balancing
                      │      │
        ┌─────────────┘      └──────────────┐
        │                                   │
   ┌────▼───────┐                    ┌─────▼──────┐
   │  Frontend  │                    │  Backend   │
   │  Next.js   │                    │  FastAPI   │
   │  (Port     │                    │  (Port     │
   │   3000)    │                    │   8000)    │
   └────────────┘                    └─────┬──────┘
                                           │
                          ┌────────────────┼────────────────┐
                          │                │                │
                     ┌────▼─────┐    ┌────▼────┐    ┌─────▼─────┐
                     │PostgreSQL│    │  Redis  │    │  Uploads  │
                     │   DB     │    │  Cache  │    │  Volume   │
                     │(Port 5432│    │(Port    │    │           │
                     │          │    │  6379)  │    │           │
                     └──────────┘    └─────────┘    └───────────┘
```

### Component Responsibilities

| Component | Purpose | Scaling Strategy |
|-----------|---------|------------------|
| Nginx | Reverse proxy, SSL termination, rate limiting | Vertical (CPU) |
| Frontend | Next.js SSR/SSG application | Horizontal (add instances) |
| Backend | FastAPI REST API, business logic | Horizontal (add instances) |
| PostgreSQL | Primary data store | Vertical (RAM/Storage) or Read replicas |
| Redis | Session cache, rate limiting | Vertical (RAM) |

## Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/CodeRenew.git
cd CodeRenew
```

### 2. Environment Configuration
```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit and fill in required values
nano backend/.env
```

### 3. Start Development Environment
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service health
docker-compose ps
```

### 4. Initialize Database
```bash
# Run migrations
./scripts/init-db.sh

# Verify migration status
cd backend && alembic current
```

### 5. Access Services
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Database: localhost:5432

## Staging Deployment

### 1. Prepare Staging Server
```bash
# SSH into staging server
ssh user@staging-server.com

# Create project directory
sudo mkdir -p /opt/coderenew
sudo chown $USER:$USER /opt/coderenew
cd /opt/coderenew
```

### 2. Clone Repository
```bash
git clone https://github.com/yourusername/CodeRenew.git .
git checkout main  # or staging branch
```

### 3. Configure Environment
```bash
# Create production environment file
cp .env.staging.example .env.staging

# Edit with staging credentials
nano .env.staging

# Set environment file
ln -sf .env.staging .env
```

### 4. SSL Certificates (Let's Encrypt)
```bash
# Install certbot
sudo apt install certbot

# Obtain certificates
sudo certbot certonly --standalone -d staging.coderenew.com -d api-staging.coderenew.com

# Link certificates for nginx
sudo ln -s /etc/letsencrypt/live/staging.coderenew.com/fullchain.pem nginx/ssl/
sudo ln -s /etc/letsencrypt/live/staging.coderenew.com/privkey.pem nginx/ssl/
sudo ln -s /etc/letsencrypt/live/staging.coderenew.com/chain.pem nginx/ssl/
```

### 5. Deploy Services
```bash
# Pull latest images
docker-compose -f docker-compose.yml -f docker-compose.staging.yml pull

# Start services
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d

# Initialize database
./scripts/init-db.sh

# Verify deployment
docker-compose ps
curl https://staging.coderenew.com/health
curl https://api-staging.coderenew.com/api/v1/health
```

### 6. Verify Deployment
```bash
# Check all services are healthy
docker-compose ps | grep -i "up (healthy)"

# Test frontend
curl -I https://staging.coderenew.com

# Test backend API
curl https://api-staging.coderenew.com/api/v1/health

# Check logs
docker-compose logs -f --tail=100
```

## Production Deployment

### Pre-Deployment Checklist
- [ ] All tests passing in CI
- [ ] Staging deployment successful and tested
- [ ] Database backup created
- [ ] Environment variables configured
- [ ] SSL certificates valid
- [ ] DNS records configured
- [ ] Monitoring/alerting configured
- [ ] Rollback plan prepared

### 1. Initial Production Setup

```bash
# SSH into production server
ssh user@production-server.com

# Create project directory
sudo mkdir -p /opt/coderenew
sudo chown $USER:$USER /opt/coderenew
cd /opt/coderenew

# Clone repository
git clone https://github.com/yourusername/CodeRenew.git .
git checkout main
```

### 2. Production Environment Configuration

```bash
# Create production environment file
cp .env.production.example .env.production

# IMPORTANT: Use strong, randomly generated values
# Generate secret key: openssl rand -hex 32
# Generate passwords: openssl rand -base64 32

# Edit with production credentials
nano .env.production

# Set environment file
ln -sf .env.production .env

# Verify no secrets are exposed
cat .env | grep -E "(PASSWORD|SECRET|KEY)" | grep -v "CHANGE_THIS"
```

### 3. SSL Certificates (Production)

```bash
# Obtain production SSL certificates
sudo certbot certonly --standalone \
  -d coderenew.com \
  -d www.coderenew.com \
  -d api.coderenew.com

# Link certificates
sudo ln -s /etc/letsencrypt/live/coderenew.com/fullchain.pem nginx/ssl/
sudo ln -s /etc/letsencrypt/live/coderenew.com/privkey.pem nginx/ssl/
sudo ln -s /etc/letsencrypt/live/coderenew.com/chain.pem nginx/ssl/

# Setup auto-renewal
sudo certbot renew --dry-run
```

### 4. Initial Database Setup

```bash
# Start database only first
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d db redis

# Wait for database to be ready
sleep 10

# Initialize database
./scripts/init-db.sh

# Create initial backup
./scripts/backup-db.sh initial
```

### 5. Deploy All Services

```bash
# Build and start all services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Monitor startup
docker-compose logs -f
```

### 6. Post-Deployment Verification

```bash
# Verify all services are running and healthy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

# Test health endpoints
curl https://coderenew.com/health
curl https://api.coderenew.com/api/v1/health

# Test authentication flow
curl -X POST https://api.coderenew.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","name":"Test User"}'

# Check logs for errors
docker-compose logs --tail=100 backend
docker-compose logs --tail=100 frontend
```

### 7. Ongoing Deployments (Updates)

```bash
# Pull latest code
cd /opt/coderenew
git pull origin main

# Create backup before deployment
./scripts/backup-db.sh pre-deploy-$(date +%Y%m%d-%H%M%S)

# Pull latest Docker images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull

# Run database migrations
./scripts/migrate-db.sh upgrade

# Restart services with zero-downtime
# Backend
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-deps --build backend

# Frontend (after backend is stable)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-deps --build frontend

# Verify deployment
curl -f https://api.coderenew.com/api/v1/health || echo "Backend health check failed!"
curl -f https://coderenew.com/health || echo "Frontend health check failed!"
```

## Database Management

### Running Migrations

```bash
# Show current migration version
cd /opt/coderenew/backend
alembic current

# Upgrade to latest
./scripts/migrate-db.sh upgrade

# Downgrade one version (if needed)
./scripts/migrate-db.sh downgrade -1
```

### Creating Backups

```bash
# Manual backup
./scripts/backup-db.sh

# Named backup
./scripts/backup-db.sh pre-major-update

# Automated backups (add to crontab)
# Daily backup at 2 AM
0 2 * * * cd /opt/coderenew && ./scripts/backup-db.sh >> /var/log/coderenew-backup.log 2>&1
```

### Restoring from Backup

```bash
# List available backups
ls -lh backups/

# Restore from backup (DESTRUCTIVE - creates backup first)
./scripts/backup-db.sh emergency-backup-$(date +%Y%m%d-%H%M%S)
./scripts/restore-db.sh backups/coderenew_backup_20250120_140000.sql.gz
```

### Connection Pooling Settings

The application uses SQLAlchemy connection pooling with these settings:
- `pool_size`: 5 connections
- `max_overflow`: 10 connections
- `pool_timeout`: 30 seconds
- `pool_recycle`: 3600 seconds (1 hour)

**For multiple application instances**, ensure PostgreSQL `max_connections` is set appropriately:
```sql
-- Calculate required connections
-- (pool_size + max_overflow) * number_of_instances + buffer
-- Example: (5 + 10) * 3 instances + 20 buffer = 65

ALTER SYSTEM SET max_connections = 100;
SELECT pg_reload_conf();
```

## Monitoring and Logging

### Log Locations

```bash
# Application logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Nginx logs
docker-compose exec nginx tail -f /var/log/nginx/access.log
docker-compose exec nginx tail -f /var/log/nginx/error.log

# Database logs
docker-compose logs -f db
```

### Health Checks

```bash
# Automated health check script
cat > /opt/coderenew/health-check.sh <<'EOF'
#!/bin/bash
SERVICES=("https://coderenew.com/health" "https://api.coderenew.com/api/v1/health")
for SERVICE in "${SERVICES[@]}"; do
  if curl -sf "$SERVICE" > /dev/null; then
    echo "[OK] $SERVICE"
  else
    echo "[FAIL] $SERVICE"
    exit 1
  fi
done
EOF

chmod +x /opt/coderenew/health-check.sh

# Add to monitoring (e.g., cron or monitoring service)
*/5 * * * * /opt/coderenew/health-check.sh || /opt/coderenew/alert.sh
```

### Performance Monitoring

```bash
# Docker stats
docker stats

# Database connections
docker-compose exec db psql -U coderenew -c "SELECT count(*) FROM pg_stat_activity;"

# Redis info
docker-compose exec redis redis-cli INFO
```

## Troubleshooting

### Common Issues

#### 1. Services Not Starting

```bash
# Check service status
docker-compose ps

# View specific service logs
docker-compose logs backend

# Restart specific service
docker-compose restart backend
```

#### 2. Database Connection Issues

```bash
# Check database is running
docker-compose ps db

# Test database connection
docker-compose exec backend python -c "from app.db.session import engine; print(engine.connect())"

# Check PostgreSQL logs
docker-compose logs db
```

#### 3. Migration Failures

```bash
# Check current migration state
cd backend && alembic current

# View migration history
alembic history

# Force set version (CAUTION)
alembic stamp head
```

#### 4. Nginx Configuration Errors

```bash
# Test nginx configuration
docker-compose exec nginx nginx -t

# Reload nginx (if config is valid)
docker-compose exec nginx nginx -s reload
```

#### 5. Out of Disk Space

```bash
# Check disk usage
df -h

# Clean up Docker
docker system prune -a --volumes

# Remove old backups
find /opt/coderenew/backups -name "*.sql.gz" -mtime +30 -delete
```

### Debug Mode

```bash
# Enable debug mode temporarily
docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
  exec -e DEBUG=True backend uvicorn app.main:app --reload

# Check detailed logs
docker-compose logs -f --tail=500 backend
```

## Rollback Procedures

### Quick Rollback (Code)

```bash
# 1. Identify previous working commit
git log --oneline -10

# 2. Revert to previous version
git checkout <previous-commit-sha>

# 3. Rebuild and restart
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# 4. Verify
curl -f https://api.coderenew.com/api/v1/health
```

### Database Rollback

```bash
# 1. Stop application
docker-compose -f docker-compose.yml -f docker-compose.prod.yml stop backend frontend

# 2. Restore database from backup
./scripts/restore-db.sh backups/coderenew_backup_YYYYMMDD_HHMMSS.sql.gz

# 3. Downgrade migrations if needed
./scripts/migrate-db.sh downgrade -1

# 4. Restart application
docker-compose -f docker-compose.yml -f docker-compose.prod.yml start backend frontend
```

### Full System Rollback

```bash
# 1. Create emergency backup
./scripts/backup-db.sh emergency-$(date +%Y%m%d-%H%M%S)

# 2. Stop all services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# 3. Restore database
./scripts/restore-db.sh backups/<last-known-good-backup>.sql.gz

# 4. Checkout previous code version
git checkout <previous-working-commit>

# 5. Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 6. Verify all services
./health-check.sh
```

## Maintenance Windows

### Planned Maintenance Procedure

1. **Announce maintenance** (24-48 hours notice)
2. **Create full backup**
3. **Enable maintenance mode** (optional: serve static page)
4. **Perform updates**
5. **Run tests**
6. **Disable maintenance mode**
7. **Monitor for issues**

```bash
# Enable maintenance mode (serve maintenance page)
docker-compose exec nginx cp /etc/nginx/maintenance.conf /etc/nginx/nginx.conf
docker-compose exec nginx nginx -s reload
```

## Security Best Practices

1. **Secrets Management**
   - Never commit `.env` files
   - Rotate secrets regularly (every 90 days)
   - Use strong random passwords (32+ characters)

2. **Access Control**
   - Use SSH keys (disable password auth)
   - Implement least privilege access
   - Regular security audits

3. **Updates**
   - Keep Docker images updated
   - Monitor security advisories
   - Apply patches promptly

4. **Backups**
   - Automated daily backups
   - Test restore procedures monthly
   - Store backups off-site

## Support & Resources

- **Documentation**: https://github.com/yourusername/CodeRenew/wiki
- **Issues**: https://github.com/yourusername/CodeRenew/issues
- **Runbook**: See DISASTER_RECOVERY.md

---

**Last Updated**: January 2025
**Version**: 1.0.0
