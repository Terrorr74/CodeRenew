# CodeRenew - Quick Reference Card

## Essential Commands

### Setup (First Time)
```bash
./scripts/setup.sh
```

### Development
```bash
# Start all services
./scripts/dev.sh start

# Stop all services
./scripts/dev.sh stop

# Restart all services
./scripts/dev.sh restart

# View logs
./scripts/dev.sh logs              # All services
./scripts/dev.sh logs backend      # Backend only
./scripts/dev.sh logs frontend     # Frontend only
```

### Database
```bash
# Run migrations
./scripts/dev.sh migrate

# Create new migration
./scripts/dev.sh migration "description"

# Reset database (WARNING: deletes all data)
./scripts/dev.sh reset

# Access database shell
./scripts/dev.sh shell db
```

### Shell Access
```bash
./scripts/dev.sh shell backend     # Backend Python shell
./scripts/dev.sh shell frontend    # Frontend Node shell
./scripts/dev.sh shell db          # PostgreSQL shell
```

### Testing
```bash
./scripts/dev.sh test backend      # Run backend tests
./scripts/dev.sh test frontend     # Run frontend tests
```

## URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

## File Locations

### Backend
```
backend/app/
├── main.py                 # FastAPI app
├── api/v1/endpoints/       # API endpoints
├── models/                 # Database models
├── schemas/                # Pydantic schemas
├── services/               # Business logic
└── core/config.py          # Configuration
```

### Frontend
```
frontend/src/
├── app/                    # Pages (App Router)
├── components/             # React components
├── lib/api/                # API client
└── types/                  # TypeScript types
```

## Common Database Models

### User
```python
email, hashed_password, is_verified
```

### Site
```python
user_id, name, url, description
```

### Scan
```python
site_id, user_id, wordpress_version_from, wordpress_version_to,
status, risk_level
```

### ScanResult
```python
scan_id, issue_type, severity, file_path, line_number,
description, recommendation
```

## API Endpoints

### Authentication
```
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

### Sites
```
GET    /api/v1/sites
POST   /api/v1/sites
GET    /api/v1/sites/{id}
PUT    /api/v1/sites/{id}
DELETE /api/v1/sites/{id}
```

### Scans
```
GET  /api/v1/scans
POST /api/v1/scans
GET  /api/v1/scans/{id}
```

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
ANTHROPIC_API_KEY=sk-ant-...
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## Docker Commands

```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs -f [service]

# Rebuild containers
docker-compose up --build

# Remove containers and volumes
docker-compose down -v

# Execute command in container
docker-compose exec backend [command]
docker-compose exec frontend [command]
```

## Troubleshooting

### Port in use
```bash
# Find process using port
lsof -ti:3000  # or 8000, 5432
# Kill the process
kill -9 [PID]
```

### Database connection error
```bash
docker-compose restart db
docker-compose logs db
```

### Clear Next.js cache
```bash
cd frontend && rm -rf .next
docker-compose restart frontend
```

### Reset everything
```bash
docker-compose down -v
./scripts/setup.sh
```

## Development Workflow

1. Start services: `./scripts/dev.sh start`
2. Make code changes (hot reload enabled)
3. Test at http://localhost:3000 or http://localhost:8000/docs
4. Create migrations if needed: `./scripts/dev.sh migration "msg"`
5. Run tests: `./scripts/dev.sh test backend`
6. Commit changes

## Documentation Files

- **README.md** - Project overview
- **GETTING_STARTED.md** - Setup guide
- **PROJECT_STRUCTURE.md** - File organization
- **PROJECT_SUMMARY.md** - What was created
- **docs/SETUP.md** - Detailed setup
- **docs/ARCHITECTURE.md** - System design
- **docs/API.md** - API reference

## Tech Stack Quick Reference

### Backend
- FastAPI, SQLAlchemy, Alembic, Pydantic
- PostgreSQL, python-jose, Anthropic SDK

### Frontend
- Next.js 14, React 18, TypeScript
- Tailwind CSS, React Hook Form, Zod, Axios

### Infrastructure
- Docker, Docker Compose, PostgreSQL

## Keyboard Shortcuts (Docker)

```bash
# Stop running container
Ctrl+C

# Detach from logs
Ctrl+P then Ctrl+Q

# View all containers
docker ps -a
```

## Next Steps

1. Update `.env` files with your API keys
2. Run `./scripts/setup.sh`
3. Access http://localhost:3000
4. Check API docs at http://localhost:8000/docs
5. Start building features!
