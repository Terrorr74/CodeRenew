# CodeRenew Setup Guide

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- Git

## Quick Start with Docker

### 1. Clone the Repository

```bash
git clone <repository-url>
cd CodeRenew
```

### 2. Configure Environment Variables

#### Backend Configuration

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` and update:
```env
DATABASE_URL=postgresql://coderenew:coderenew_dev_password@db:5432/coderenew
SECRET_KEY=your-super-secret-key-change-this-in-production
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

#### Frontend Configuration

```bash
cd ../frontend
cp .env.example .env.local
```

Edit `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### 3. Start the Application

```bash
cd ..  # Back to project root
docker-compose up --build
```

This will start:
- PostgreSQL on port 5432
- Backend API on port 8000
- Frontend on port 3000

### 4. Initialize the Database

In a new terminal:

```bash
docker-compose exec backend alembic upgrade head
```

### 5. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Local Development (Without Docker)

### Backend Setup

1. **Create Virtual Environment**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure Environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Setup Database**:

Make sure PostgreSQL is running locally, then:
```bash
# Create database
createdb coderenew

# Run migrations
alembic upgrade head
```

5. **Start the Backend**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Install Dependencies**:
```bash
cd frontend
npm install
```

2. **Configure Environment**:
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

3. **Start the Frontend**:
```bash
npm run dev
```

## Database Migrations

### Create a New Migration

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

### View Migration History

```bash
alembic history
```

## Common Issues

### Port Already in Use

If ports 3000, 8000, or 5432 are already in use:

1. Stop the conflicting service, or
2. Change the port mapping in `docker-compose.yml`

### Database Connection Error

Make sure PostgreSQL is running:
```bash
docker-compose ps
```

Check database logs:
```bash
docker-compose logs db
```

### Frontend Can't Connect to Backend

1. Check backend is running: http://localhost:8000/health
2. Verify NEXT_PUBLIC_API_URL in frontend/.env.local
3. Check CORS settings in backend/app/main.py

### Migration Errors

Reset the database (development only):
```bash
docker-compose down -v
docker-compose up -d db
docker-compose exec backend alembic upgrade head
```

## Development Tools

### View Backend Logs

```bash
docker-compose logs -f backend
```

### View Frontend Logs

```bash
docker-compose logs -f frontend
```

### Access Database

```bash
docker-compose exec db psql -U coderenew -d coderenew
```

### Run Backend Tests

```bash
cd backend
pytest
```

### Run Frontend Type Check

```bash
cd frontend
npm run type-check
```

### Format Code

Backend (Black):
```bash
cd backend
black .
```

Frontend (ESLint):
```bash
cd frontend
npm run lint
```

## Production Deployment

Production deployment instructions will be added as the project evolves.

Key considerations:
- Use secure SECRET_KEY
- Use managed PostgreSQL
- Enable HTTPS
- Set DEBUG=False
- Use production-grade web server (Gunicorn/Nginx)
- Implement proper logging
- Set up monitoring
- Regular backups
