# Contributing to CodeRenew

Welcome to the CodeRenew project! We appreciate your interest in contributing. This document provides guidelines and instructions for setting up your development environment and contributing to the codebase.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker & Docker Compose**: For running the application in containers.
- **Python 3.11+**: For backend development (if running locally without Docker).
- **Node.js 18+**: For frontend development (if running locally without Docker).
- **Git**: For version control.

## Development Workflow

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/CodeRenew.git
cd CodeRenew
```

### 2. Environment Setup

Create the necessary environment files from the examples:

```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env
```

**Important**: You will need an Anthropic API key for the AI features to work. Add it to `backend/.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Start the Application

The easiest way to run the full stack is using Docker Compose:

```bash
docker-compose up -d
```

This will start:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **PostgreSQL**: Database service

### 4. Database Migrations

After starting the containers, apply the database migrations:

```bash
docker-compose exec backend alembic upgrade head
```

## Project Structure

- **`backend/`**: FastAPI application (Python)
- **`frontend/`**: Next.js application (TypeScript/React)
- **`tests/`**: Test suites
- **`docs/`**: Project documentation

## Testing

We maintain high test coverage. Please ensure all tests pass before submitting a PR.

### Backend Tests
See [BACKEND_TEST_PLAN.md](BACKEND_TEST_PLAN.md) for detailed instructions.

```bash
# Run all backend tests
docker-compose exec backend pytest
```

### Frontend Tests
See [FRONTEND_TEST_PLAN.md](FRONTEND_TEST_PLAN.md) for detailed instructions.

```bash
# Run frontend tests
cd frontend
npm test
```

## Code Style

### Backend (Python)
We use `black` for formatting and `isort` for import sorting.
```bash
# Format code
docker-compose exec backend black .
docker-compose exec backend isort .
```

### Frontend (TypeScript)
We use `ESLint` and `Prettier`.
```bash
# Lint and format
cd frontend
npm run lint
```

## Git Workflow

1. **Create a Branch**: Create a new branch for your feature or fix.
   - `feature/my-new-feature`
   - `fix/bug-description`
2. **Commit Changes**: Write clear, descriptive commit messages.
3. **Push**: Push your branch to the repository.
4. **Pull Request**: Open a Pull Request (PR) against the `develop` branch.

## Documentation

- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md) for system design details.
- **Deployment**: See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions.

Thank you for contributing!
