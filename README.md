# CodeRenew

A WordPress compatibility scanner SaaS application that analyzes WordPress sites for compatibility issues when upgrading between versions.

## Technology Stack

- **Frontend**: Next.js 14+ (App Router), TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python 3.11+), SQLAlchemy, Alembic
- **Database**: PostgreSQL
- **Authentication**: Custom JWT with python-jose
- **AI**: Anthropic Claude API
- **File Storage**: Local filesystem (MVP)
- **Development**: Docker Compose

## Project Structure

```
CodeRenew/
├── frontend/           # Next.js application
├── backend/            # FastAPI application
├── docs/               # Documentation
├── scripts/            # Utility scripts
└── docker-compose.yml  # Docker orchestration
```

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- PostgreSQL 15+ (if running locally without Docker)

## Quick Start

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd CodeRenew
```

2. Copy environment files:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

3. Update environment variables in both `.env` files with your configuration:
   - Database credentials
   - Anthropic API key
   - JWT secret
   - Frontend API URL

4. Start the application:
```bash
docker-compose up --build
```

5. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development

#### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Update .env with your configuration
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
# Update .env.local with your configuration
npm run dev
```

## Database Migrations

Create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

### Backend (.env)

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `ANTHROPIC_API_KEY`: Claude API key
- `ALGORITHM`: JWT algorithm (HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `UPLOAD_DIR`: Directory for file uploads

### Frontend (.env.local)

- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_APP_URL`: Frontend URL

## Development Workflow

1. Create a feature branch from `main`
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

Deployment instructions will be added as the project evolves.

## License

[Your License]

## Contributors

[Your Team]
