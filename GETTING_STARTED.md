# Getting Started with CodeRenew

Welcome to CodeRenew! This guide will help you get up and running quickly.

## What is CodeRenew?

CodeRenew is a WordPress compatibility scanner SaaS application that helps developers analyze their WordPress themes and plugins for compatibility issues when upgrading between WordPress versions. It uses Claude AI to provide intelligent analysis and recommendations.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker Desktop** (recommended) - [Download](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download](https://git-scm.com/downloads)
- **Anthropic API Key** - [Get one here](https://console.anthropic.com/)

### Optional (for local development without Docker):
- Node.js 18+ - [Download](https://nodejs.org/)
- Python 3.11+ - [Download](https://www.python.org/downloads/)
- PostgreSQL 15+ - [Download](https://www.postgresql.org/download/)

## Quick Start (5 minutes)

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd CodeRenew
```

### 2. Configure Environment

The project includes example environment files. You'll need to update them with your settings.

#### Backend Configuration

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` and update these critical values:

```env
# Generate a secure secret key (or use: openssl rand -hex 32)
SECRET_KEY=your-super-secret-key-here-change-this

# Add your Anthropic API key
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# Database URL (keep this for Docker setup)
DATABASE_URL=postgresql://coderenew:coderenew_dev_password@db:5432/coderenew
```

#### Frontend Configuration

```bash
cd ../frontend
cp .env.example .env.local
```

The default values should work for local development:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### 3. Start the Application

From the project root directory:

```bash
cd ..  # Return to project root
./scripts/setup.sh
```

This will:
- Create environment files if they don't exist
- Start all Docker containers
- Wait for the database to be ready
- Run database migrations

### 4. Access the Application

Once setup is complete, you can access:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs**: http://localhost:8000/redoc

## First Steps

### 1. Create an Account

1. Navigate to http://localhost:3000
2. Click "Get Started" or "Sign Up"
3. Enter your email and password
4. Click "Create Account"

### 2. Login

1. After registration, you'll be redirected to the login page
2. Enter your credentials
3. Click "Sign In"

### 3. Add a WordPress Site

1. From the dashboard, click "Manage Sites"
2. Click "Add Site" (to be implemented)
3. Enter site details
4. Save the site

### 4. Run Your First Scan

1. Click "New Scan" from the dashboard
2. Select a site
3. Choose WordPress versions (from → to)
4. Upload theme/plugin files (to be implemented)
5. Start the scan

## Project Structure Overview

```
CodeRenew/
├── backend/          # FastAPI application
├── frontend/         # Next.js application
├── docs/             # Documentation
├── scripts/          # Helper scripts
└── docker-compose.yml
```

### Key Files

- **README.md**: Project overview
- **PROJECT_STRUCTURE.md**: Detailed file structure
- **docs/SETUP.md**: Comprehensive setup guide
- **docs/ARCHITECTURE.md**: Architecture documentation
- **docs/API.md**: API reference

## Development Commands

The project includes helper scripts for common tasks:

### Start Development Environment
```bash
./scripts/dev.sh start
```

### Stop All Services
```bash
./scripts/dev.sh stop
```

### View Logs
```bash
./scripts/dev.sh logs           # All services
./scripts/dev.sh logs backend   # Backend only
./scripts/dev.sh logs frontend  # Frontend only
```

### Database Operations

**Run Migrations**:
```bash
./scripts/dev.sh migrate
```

**Create New Migration**:
```bash
./scripts/dev.sh migration "add user preferences table"
```

**Reset Database** (WARNING: Deletes all data):
```bash
./scripts/dev.sh reset
```

### Access Shell

**Backend Shell**:
```bash
./scripts/dev.sh shell backend
```

**Frontend Shell**:
```bash
./scripts/dev.sh shell frontend
```

**Database Shell**:
```bash
./scripts/dev.sh shell db
```

### Run Tests

**Backend Tests**:
```bash
./scripts/dev.sh test backend
```

**Frontend Tests**:
```bash
./scripts/dev.sh test frontend
```

## Making Your First Code Change

### Backend Example: Add a New API Endpoint

1. Create a new endpoint in `backend/app/api/v1/endpoints/`
2. Define Pydantic schemas in `backend/app/schemas/`
3. Add business logic in `backend/app/services/`
4. Test at http://localhost:8000/docs

### Frontend Example: Add a New Page

1. Create a new file in `frontend/src/app/` (App Router)
2. Build components in `frontend/src/components/`
3. Add API calls in `frontend/src/lib/api/`
4. View at http://localhost:3000

## Common Issues and Solutions

### Port Already in Use

**Problem**: Docker complains that ports 3000, 8000, or 5432 are in use.

**Solution**:
```bash
# Stop any running services on those ports, or
# Change port mappings in docker-compose.yml
```

### Database Connection Error

**Problem**: Backend can't connect to the database.

**Solution**:
```bash
# Check if database is running
docker-compose ps

# View database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Frontend Build Errors

**Problem**: Next.js build fails.

**Solution**:
```bash
# Clear Next.js cache
cd frontend
rm -rf .next

# Restart frontend container
docker-compose restart frontend
```

### Migration Errors

**Problem**: Alembic migration fails.

**Solution**:
```bash
# Check current migration status
docker-compose exec backend alembic current

# View migration history
docker-compose exec backend alembic history

# If needed, reset database (dev only)
./scripts/dev.sh reset
```

## Learning Resources

### Backend (FastAPI + Python)

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

### Frontend (Next.js + TypeScript)

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)

### Claude AI

- [Anthropic Documentation](https://docs.anthropic.com/)
- [Claude API Reference](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)

## Getting Help

If you encounter issues:

1. Check the [SETUP.md](docs/SETUP.md) for detailed setup instructions
2. Review [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
3. Consult [API.md](docs/API.md) for API documentation
4. Check Docker logs: `docker-compose logs`

## Next Steps

Now that you're set up, you can:

1. Explore the codebase structure (see PROJECT_STRUCTURE.md)
2. Review the API documentation at http://localhost:8000/docs
3. Start building features (see docs/ARCHITECTURE.md for guidance)
4. Write tests for your code
5. Contribute to the project

## Production Deployment

For production deployment guidance, see the deployment section in docs/ARCHITECTURE.md.

Key considerations:
- Use secure environment variables
- Enable HTTPS
- Use managed database service
- Set up monitoring and logging
- Implement backup strategy

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]

---

Happy coding! If you have questions or suggestions, please open an issue.
