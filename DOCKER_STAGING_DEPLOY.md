# EPSS Integration - Docker Staging Deployment

**Environment:** Staging (Docker)
**Deployment Time:** 30-45 minutes
**Method:** Docker Compose

---

## 🐳 Docker Deployment Overview

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Docker Compose Stack                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Frontend   │  │   Backend    │  │    Celery    │  │
│  │   (Next.js)  │  │  (FastAPI)   │  │   Worker     │  │
│  │   Port 3000  │  │   Port 8000  │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Celery     │  │  PostgreSQL  │  │    Redis     │  │
│  │    Beat      │  │   Port 5432  │  │  Port 6379   │  │
│  │              │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Prerequisites

### Required Software

```bash
# Check Docker and Docker Compose are installed
docker --version
# Expected: Docker version 20.10.0 or higher

docker-compose --version
# Expected: Docker Compose version 1.29.0 or higher
```

### Install if Missing

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# macOS
brew install docker docker-compose

# Start Docker daemon
sudo systemctl start docker
sudo systemctl enable docker
```

---

## 🚀 Quick Deployment (5 Steps)

### Step 1: SSH into Staging Server

```bash
ssh deploy@staging.coderenew.com
```

### Step 2: Navigate to Project & Pull Code

```bash
cd /var/www/coderenew

# Backup current deployment
docker-compose -f docker-compose.staging.yml down
docker-compose -f docker-compose.staging.yml ps

# Pull latest code
git pull origin main

# Verify EPSS files exist
ls -la backend/app/services/epss/
ls -la backend/alembic/versions/007_add_epss_fields.py
```

### Step 3: Build New Images with EPSS Integration

```bash
# Build all services
docker-compose -f docker-compose.staging.yml build

# Or build specific services
docker-compose -f docker-compose.staging.yml build backend
docker-compose -f docker-compose.staging.yml build frontend
docker-compose -f docker-compose.staging.yml build celery-worker
```

### Step 4: Run Database Migration

```bash
# Start database first (if not running)
docker-compose -f docker-compose.staging.yml up -d postgres

# Wait for database to be ready
sleep 5

# Run migration
docker-compose -f docker-compose.staging.yml run --rm backend \
  alembic upgrade head

# Verify migration
docker-compose -f docker-compose.staging.yml run --rm backend \
  alembic current
```

### Step 5: Start All Services

```bash
# Start all services in detached mode
docker-compose -f docker-compose.staging.yml up -d

# Check all services are running
docker-compose -f docker-compose.staging.yml ps

# Expected output:
# NAME                STATUS              PORTS
# backend             Up                  0.0.0.0:8000->8000/tcp
# frontend            Up                  0.0.0.0:3000->3000/tcp
# celery-worker       Up
# celery-beat         Up
# postgres            Up                  5432/tcp
# redis               Up                  6379/tcp
```

---

## 📝 Docker Compose Configuration

### Complete docker-compose.staging.yml

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: coderenew-postgres-staging
    environment:
      POSTGRES_DB: coderenew_staging
      POSTGRES_USER: coderenew
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data_staging:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U coderenew"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - coderenew-staging

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: coderenew-redis-staging
    ports:
      - "6379:6379"
    volumes:
      - redis_data_staging:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - coderenew-staging

  # Backend API (FastAPI)
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      args:
        BUILD_ENV: staging
    container_name: coderenew-backend-staging
    environment:
      DATABASE_URL: postgresql://coderenew:${POSTGRES_PASSWORD}@postgres:5432/coderenew_staging
      REDIS_URL: redis://redis:6379/0
      ENVIRONMENT: staging
      SECRET_KEY: ${SECRET_KEY}
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/0
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - backend_uploads_staging:/app/uploads
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - coderenew-staging

  # Celery Worker (EPSS enrichment tasks)
  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: coderenew-celery-worker-staging
    environment:
      DATABASE_URL: postgresql://coderenew:${POSTGRES_PASSWORD}@postgres:5432/coderenew_staging
      REDIS_URL: redis://redis:6379/0
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/0
      ENVIRONMENT: staging
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    command: celery -A app.core.celery_app worker --loglevel=info
    networks:
      - coderenew-staging

  # Celery Beat (Scheduled tasks - EPSS daily refresh)
  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: coderenew-celery-beat-staging
    environment:
      DATABASE_URL: postgresql://coderenew:${POSTGRES_PASSWORD}@postgres:5432/coderenew_staging
      REDIS_URL: redis://redis:6379/0
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/0
      ENVIRONMENT: staging
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    command: celery -A app.core.celery_app beat --loglevel=info
    networks:
      - coderenew-staging

  # Frontend (Next.js)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        BUILD_ENV: staging
        NEXT_PUBLIC_API_URL: http://staging.coderenew.com/api
    container_name: coderenew-frontend-staging
    environment:
      NEXT_PUBLIC_API_URL: http://staging.coderenew.com/api
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    command: npm run start
    networks:
      - coderenew-staging

volumes:
  postgres_data_staging:
  redis_data_staging:
  backend_uploads_staging:

networks:
  coderenew-staging:
    driver: bridge
```

---

## 🔧 Backend Dockerfile

### backend/Dockerfile

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install httpx for EPSS integration
RUN pip install --no-cache-dir httpx

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 8000

# Default command (can be overridden)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🎨 Frontend Dockerfile

### frontend/Dockerfile

```dockerfile
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build argument for environment
ARG BUILD_ENV=staging
ARG NEXT_PUBLIC_API_URL

ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NODE_ENV=production

# Build Next.js application
RUN npm run build

# Expose port
EXPOSE 3000

# Start Next.js
CMD ["npm", "run", "start"]
```

---

## 🔐 Environment Variables

### .env.staging

Create `.env.staging` file:

```bash
# Database
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://coderenew:your_secure_password_here@postgres:5432/coderenew_staging

# Redis
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Application
ENVIRONMENT=staging
SECRET_KEY=your_secret_key_here
DEBUG=False

# API URLs
API_URL=http://backend:8000
NEXT_PUBLIC_API_URL=http://staging.coderenew.com/api

# EPSS Configuration (optional)
EPSS_API_URL=https://api.first.org/data/v1/epss
EPSS_CACHE_TTL_HOURS=24
```

---

## ✅ Verification Steps

### 1. Check All Containers Running

```bash
docker-compose -f docker-compose.staging.yml ps

# Expected: All services "Up"
```

### 2. Check Logs

```bash
# View all logs
docker-compose -f docker-compose.staging.yml logs -f

# View specific service logs
docker-compose -f docker-compose.staging.yml logs -f backend
docker-compose -f docker-compose.staging.yml logs -f celery-worker
docker-compose -f docker-compose.staging.yml logs -f frontend

# Check for EPSS-related logs
docker-compose -f docker-compose.staging.yml logs backend | grep -i epss
```

### 3. Test Database Migration

```bash
# Check migration status
docker-compose -f docker-compose.staging.yml exec backend \
  alembic current

# Expected output: 007 (head)

# Verify EPSS columns exist
docker-compose -f docker-compose.staging.yml exec postgres \
  psql -U coderenew -d coderenew_staging -c "\d scan_results" | grep epss

# Expected: 4 EPSS columns (cve_id, epss_score, epss_percentile, epss_updated_at)
```

### 4. Test EPSS Service

```bash
# Enter backend container
docker-compose -f docker-compose.staging.yml exec backend bash

# Test EPSS service
python3 << 'EOF'
import asyncio
from app.services.epss import get_epss_service

async def test():
    epss = get_epss_service()
    score = await epss.get_epss_score('CVE-2021-44228')
    if score:
        print(f"✅ EPSS Service Working!")
        print(f"   CVE: {score.cve}")
        print(f"   Score: {score.epss_score:.4f}")
        print(f"   Percentile: {score.percentile:.4f}")
    else:
        print("❌ EPSS Service Failed!")

asyncio.run(test())
EOF

# Exit container
exit
```

### 5. Test API Endpoints

```bash
# Health check
curl http://localhost:8000/api/health

# Get scans (with EPSS data)
curl http://localhost:8000/api/v1/scans/1 | jq '.results[0] | {cve_id, epss_score, epss_percentile}'
```

### 6. Test Frontend

```bash
# Open in browser
open http://localhost:3000

# Or test with curl
curl http://localhost:3000 | grep -i epss
```

### 7. Test Celery Tasks

```bash
# Check Celery worker is running
docker-compose -f docker-compose.staging.yml exec celery-worker \
  celery -A app.core.celery_app inspect active

# Trigger EPSS enrichment task manually
docker-compose -f docker-compose.staging.yml exec celery-worker \
  celery -A app.core.celery_app call \
  app.tasks.epss_tasks.enrich_scan_results_with_epss --args='[1]'

# Check task completed
docker-compose -f docker-compose.staging.yml logs celery-worker | tail -20
```

---

## 🔄 Database Backup & Restore

### Backup Before Deployment

```bash
# Backup database
docker-compose -f docker-compose.staging.yml exec postgres \
  pg_dump -U coderenew coderenew_staging > \
  backup_staging_$(date +%Y%m%d_%H%M%S).sql

# Verify backup
ls -lh backup_staging_*.sql
```

### Restore if Needed

```bash
# Stop services
docker-compose -f docker-compose.staging.yml down

# Start only database
docker-compose -f docker-compose.staging.yml up -d postgres

# Wait for database
sleep 5

# Restore database
cat backup_staging_*.sql | \
  docker-compose -f docker-compose.staging.yml exec -T postgres \
  psql -U coderenew coderenew_staging

# Restart all services
docker-compose -f docker-compose.staging.yml up -d
```

---

## 🚨 Rollback Procedure

### Quick Rollback

```bash
# 1. Stop all services
docker-compose -f docker-compose.staging.yml down

# 2. Checkout previous version
git checkout HEAD~1

# 3. Rebuild images with old code
docker-compose -f docker-compose.staging.yml build

# 4. Rollback database migration
docker-compose -f docker-compose.staging.yml up -d postgres
docker-compose -f docker-compose.staging.yml run --rm backend \
  alembic downgrade -1

# 5. Start all services
docker-compose -f docker-compose.staging.yml up -d

# 6. Verify
docker-compose -f docker-compose.staging.yml ps
curl http://localhost:8000/api/health
```

---

## 📊 Performance Monitoring

### Resource Usage

```bash
# Check container resource usage
docker stats

# Expected:
# CONTAINER              CPU %     MEM USAGE / LIMIT
# backend                1-5%      200-500MB
# celery-worker          0.5-2%    150-300MB
# celery-beat            0.1-0.5%  100-200MB
# frontend               1-3%      200-400MB
# postgres               1-5%      100-300MB
# redis                  0.5-2%    50-100MB
```

### Log Analysis

```bash
# EPSS API calls
docker-compose -f docker-compose.staging.yml logs backend | \
  grep "EPSS API" | tail -20

# Error rate
docker-compose -f docker-compose.staging.yml logs backend | \
  grep -i error | wc -l

# Celery task success
docker-compose -f docker-compose.staging.yml logs celery-worker | \
  grep "succeeded" | wc -l
```

---

## 🛠️ Troubleshooting

### Container Won't Start

```bash
# Check logs for errors
docker-compose -f docker-compose.staging.yml logs backend

# Common issues:
# 1. Database not ready - wait and retry
# 2. Port already in use - check: netstat -tulpn | grep 8000
# 3. Environment variables missing - check .env.staging
```

### Migration Fails

```bash
# Check database connection
docker-compose -f docker-compose.staging.yml exec postgres \
  psql -U coderenew -d coderenew_staging -c "SELECT 1;"

# Check migration history
docker-compose -f docker-compose.staging.yml run --rm backend \
  alembic history

# Try migration again
docker-compose -f docker-compose.staging.yml run --rm backend \
  alembic upgrade head
```

### EPSS Service Not Working

```bash
# Check internet connectivity from container
docker-compose -f docker-compose.staging.yml exec backend \
  curl https://api.first.org/data/v1/epss?cve=CVE-2021-44228

# Check httpx is installed
docker-compose -f docker-compose.staging.yml exec backend \
  pip list | grep httpx

# Reinstall if missing
docker-compose -f docker-compose.staging.yml exec backend \
  pip install httpx
```

---

## 📋 Deployment Checklist

**Pre-Deployment:**
- [ ] Docker and Docker Compose installed
- [ ] `.env.staging` file configured
- [ ] Database backup completed
- [ ] Latest code pulled from git

**Deployment:**
- [ ] Images built successfully
- [ ] Database migration completed
- [ ] All containers running
- [ ] Health checks passing

**Verification:**
- [ ] API responding (curl http://localhost:8000/api/health)
- [ ] EPSS service working (test with Python script)
- [ ] Frontend accessible (http://localhost:3000)
- [ ] Celery tasks executing
- [ ] Database has EPSS columns
- [ ] No errors in logs

**Post-Deployment:**
- [ ] Monitor logs for 1 hour
- [ ] Test EPSS feature in browser
- [ ] Verify performance metrics
- [ ] Document any issues

---

## 🎯 Quick Commands Reference

```bash
# Start all services
docker-compose -f docker-compose.staging.yml up -d

# Stop all services
docker-compose -f docker-compose.staging.yml down

# Rebuild and restart
docker-compose -f docker-compose.staging.yml up -d --build

# View logs
docker-compose -f docker-compose.staging.yml logs -f

# Run migration
docker-compose -f docker-compose.staging.yml run --rm backend alembic upgrade head

# Execute command in container
docker-compose -f docker-compose.staging.yml exec backend bash

# Restart single service
docker-compose -f docker-compose.staging.yml restart backend

# Remove all containers and volumes
docker-compose -f docker-compose.staging.yml down -v
```

---

**Docker deployment is container-isolated and easily rollback-able! 🐳**
