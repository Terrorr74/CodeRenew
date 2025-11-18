# CodeRenew Architecture

## Overview

CodeRenew is a WordPress compatibility scanner built as a modern full-stack SaaS application using a monorepo structure.

## Technology Stack

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Forms**: React Hook Form + Zod
- **HTTP Client**: Axios
- **State Management**: React Hooks (future: React Query)

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Authentication**: JWT with python-jose
- **AI Integration**: Anthropic Claude API

### Database
- **Primary Database**: PostgreSQL 15+
- **Schema**:
  - users (authentication)
  - sites (WordPress sites)
  - scans (scan metadata)
  - scan_results (detailed findings)

### Infrastructure
- **Development**: Docker Compose
- **Storage**: Local filesystem (MVP)

## Project Structure

```
CodeRenew/
├── frontend/                 # Next.js application
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   ├── components/      # React components
│   │   ├── lib/             # Utilities and API client
│   │   ├── types/           # TypeScript definitions
│   │   └── styles/          # Global styles
│   └── public/              # Static assets
│
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── api/             # API routes
│   │   ├── core/            # Core configuration
│   │   ├── db/              # Database configuration
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   └── middleware/      # Middleware
│   ├── alembic/             # Database migrations
│   └── uploads/             # File uploads
│
├── docs/                     # Documentation
├── scripts/                  # Utility scripts
└── docker-compose.yml        # Docker orchestration
```

## Architecture Patterns

### Backend Architecture

**Layer Structure:**
1. **API Layer** (`app/api/`): HTTP endpoints and request handling
2. **Service Layer** (`app/services/`): Business logic and external integrations
3. **Data Layer** (`app/models/`): Database models and ORM
4. **Schema Layer** (`app/schemas/`): Request/response validation

**Key Patterns:**
- Dependency injection with FastAPI's `Depends()`
- Repository pattern for database access
- Service layer for business logic encapsulation
- Pydantic models for validation

### Frontend Architecture

**Structure:**
- App Router for file-based routing
- Client/Server component separation
- API client layer for backend communication
- Shared component library

**Key Patterns:**
- Server-side rendering (SSR) where appropriate
- Client-side state with React hooks
- Form validation with Zod schemas
- Reusable UI components

## Data Flow

### Authentication Flow
1. User submits credentials to frontend
2. Frontend sends POST to `/api/v1/auth/login`
3. Backend validates credentials and returns JWT
4. Frontend stores token in localStorage
5. Subsequent requests include token in Authorization header

### Scan Creation Flow
1. User uploads files or provides site info
2. Frontend creates scan record via API
3. Backend saves scan metadata to database
4. Background task processes files:
   - Extract PHP files
   - Analyze code for issues
   - Use Claude API for advanced analysis
   - Store results in database
5. Frontend polls for scan completion

## Security Considerations

### Authentication
- JWT tokens with expiration
- Password hashing with bcrypt
- HTTPS in production
- CORS configuration

### Data Protection
- Input validation with Pydantic
- SQL injection prevention via ORM
- File upload validation
- Rate limiting (future)

### API Security
- Authentication required for protected endpoints
- User-scoped data access
- Secure environment variable handling

## Scalability Considerations

### Current MVP Approach
- Single-server deployment
- Local file storage
- Synchronous processing

### Future Enhancements
- Background job queue (Celery/Redis)
- Object storage (S3)
- Horizontal scaling
- Caching layer (Redis)
- CDN for static assets

## Development Workflow

1. **Local Development**:
   - Use Docker Compose for all services
   - Hot reload enabled for both frontend and backend
   - PostgreSQL in container

2. **Database Changes**:
   - Create models in `backend/app/models/`
   - Generate migration: `alembic revision --autogenerate`
   - Review and apply: `alembic upgrade head`

3. **API Development**:
   - Define Pydantic schemas
   - Create endpoint in appropriate router
   - Implement service layer logic
   - Test via Swagger UI

4. **Frontend Development**:
   - Create/update page in `app/` directory
   - Build components in `components/`
   - Add API methods in `lib/api/`
   - Type with TypeScript

## Testing Strategy

### Backend Tests
- Unit tests for services
- Integration tests for API endpoints
- Database test fixtures
- Use pytest

### Frontend Tests
- Component tests with React Testing Library
- Integration tests for user flows
- E2E tests (future: Playwright/Cypress)

## Monitoring and Logging

### Logging
- Backend: Python logging module
- Frontend: Console logs (development)
- Structured logging for production

### Error Tracking
- Future: Sentry integration
- API error responses with details
- User-friendly error messages

## Deployment

### MVP Deployment
- Single Docker host
- Docker Compose for orchestration
- Environment variables for configuration
- PostgreSQL in container (acceptable for MVP)

### Production Considerations
- Managed PostgreSQL database
- Container orchestration (Kubernetes/ECS)
- Load balancer
- SSL/TLS certificates
- CDN integration
- Backup strategy
