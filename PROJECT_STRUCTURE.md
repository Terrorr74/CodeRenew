# CodeRenew - Project Structure

## Complete Directory Tree

```
CodeRenew/
├── README.md                          # Main project documentation
├── docker-compose.yml                 # Docker orchestration
├── .gitignore                         # Git ignore patterns
│
├── backend/                           # FastAPI Backend Application
│   ├── Dockerfile                     # Backend Docker configuration
│   ├── .dockerignore                  # Docker ignore patterns
│   ├── .env.example                   # Environment variables template
│   ├── requirements.txt               # Python dependencies
│   ├── alembic.ini                    # Alembic configuration
│   │
│   ├── alembic/                       # Database migrations
│   │   ├── README                     # Migration guide
│   │   ├── env.py                     # Alembic environment
│   │   ├── script.py.mako             # Migration template
│   │   └── versions/                  # Migration files (auto-generated)
│   │
│   ├── app/                           # Main application code
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app initialization
│   │   │
│   │   ├── api/                       # API layer
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py        # Shared dependencies (auth, etc.)
│   │   │   └── v1/                    # API version 1
│   │   │       ├── __init__.py
│   │   │       ├── api.py             # Router aggregation
│   │   │       └── endpoints/         # API endpoints
│   │   │           ├── __init__.py
│   │   │           ├── auth.py        # Authentication endpoints
│   │   │           ├── sites.py       # Sites CRUD endpoints
│   │   │           └── scans.py       # Scans endpoints
│   │   │
│   │   ├── core/                      # Core configuration
│   │   │   ├── __init__.py
│   │   │   ├── config.py              # Settings management
│   │   │   └── security.py            # JWT and password utilities
│   │   │
│   │   ├── db/                        # Database configuration
│   │   │   ├── __init__.py
│   │   │   └── session.py             # SQLAlchemy session
│   │   │
│   │   ├── models/                    # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Base model
│   │   │   ├── user.py                # User model
│   │   │   ├── site.py                # Site model
│   │   │   ├── scan.py                # Scan model
│   │   │   └── scan_result.py         # ScanResult model
│   │   │
│   │   ├── schemas/                   # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py                # User schemas
│   │   │   ├── site.py                # Site schemas
│   │   │   └── scan.py                # Scan schemas
│   │   │
│   │   ├── services/                  # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── wordpress/             # WordPress scanning
│   │   │   │   ├── __init__.py
│   │   │   │   └── scanner.py         # Scanner service
│   │   │   ├── claude/                # Claude AI integration
│   │   │   │   ├── __init__.py
│   │   │   │   └── client.py          # Claude API client
│   │   │   └── file_processor/        # File processing
│   │   │       ├── __init__.py
│   │   │       └── extractor.py       # File extraction
│   │   │
│   │   └── middleware/                # Custom middleware
│   │       └── __init__.py
│   │
│   ├── uploads/                       # File upload directory
│   │   └── .gitkeep                   # Keep directory in git
│   │
│   └── tests/                         # Test files (to be created)
│
├── frontend/                          # Next.js Frontend Application
│   ├── Dockerfile                     # Frontend Docker configuration
│   ├── .dockerignore                  # Docker ignore patterns
│   ├── .env.example                   # Environment variables template
│   ├── package.json                   # Node dependencies
│   ├── tsconfig.json                  # TypeScript configuration
│   ├── tailwind.config.ts             # Tailwind CSS configuration
│   ├── postcss.config.js              # PostCSS configuration
│   ├── next.config.js                 # Next.js configuration
│   ├── .eslintrc.json                 # ESLint configuration
│   │
│   ├── public/                        # Static assets
│   │   └── favicon.ico                # Favicon
│   │
│   └── src/                           # Source code
│       ├── app/                       # Next.js App Router
│       │   ├── layout.tsx             # Root layout
│       │   ├── page.tsx               # Home page
│       │   │
│       │   ├── auth/                  # Authentication pages
│       │   │   ├── login/
│       │   │   │   └── page.tsx       # Login page
│       │   │   ├── register/
│       │   │   │   └── page.tsx       # Registration page
│       │   │   └── verify/            # Email verification (to be added)
│       │   │
│       │   ├── dashboard/             # Dashboard pages
│       │   │   ├── page.tsx           # Dashboard home
│       │   │   ├── sites/             # Sites management (to be added)
│       │   │   └── history/           # Scan history (to be added)
│       │   │
│       │   ├── scans/                 # Scan pages
│       │   │   ├── new/               # New scan page (to be added)
│       │   │   └── [id]/              # Scan details (to be added)
│       │   │
│       │   └── api/                   # API routes (if needed)
│       │       └── auth/              # Auth endpoints
│       │
│       ├── components/                # React components
│       │   ├── ui/                    # UI components
│       │   │   └── .gitkeep
│       │   ├── forms/                 # Form components
│       │   │   ├── LoginForm.tsx
│       │   │   └── RegisterForm.tsx
│       │   ├── layouts/               # Layout components
│       │   │   └── DashboardLayout.tsx
│       │   └── dashboard/             # Dashboard components (to be added)
│       │
│       ├── lib/                       # Utilities and libraries
│       │   ├── api/                   # API client
│       │   │   ├── index.ts           # Export all
│       │   │   ├── client.ts          # Axios client
│       │   │   ├── auth.ts            # Auth API
│       │   │   ├── sites.ts           # Sites API
│       │   │   └── scans.ts           # Scans API
│       │   ├── utils/                 # Utility functions
│       │   │   └── cn.ts              # Class name utility
│       │   └── hooks/                 # Custom React hooks
│       │       └── .gitkeep
│       │
│       ├── types/                     # TypeScript type definitions
│       │   └── index.ts               # Shared types
│       │
│       └── styles/                    # Global styles
│           └── globals.css            # Global CSS with Tailwind
│
├── docs/                              # Documentation
│   ├── ARCHITECTURE.md                # Architecture documentation
│   ├── API.md                         # API documentation
│   └── SETUP.md                       # Setup guide
│
└── scripts/                           # Utility scripts
    ├── setup.sh                       # Initial setup script
    └── dev.sh                         # Development helper script
```

## Key Files and Their Purpose

### Backend

- **app/main.py**: FastAPI application entry point, middleware, and router configuration
- **app/core/config.py**: Environment-based configuration using Pydantic Settings
- **app/core/security.py**: JWT token creation/validation and password hashing
- **app/db/session.py**: Database connection and session management
- **app/models/**: SQLAlchemy ORM models for database tables
- **app/schemas/**: Pydantic models for request/response validation
- **app/api/dependencies.py**: Shared dependencies like authentication
- **app/api/v1/endpoints/**: API endpoint implementations
- **app/services/**: Business logic and external service integrations

### Frontend

- **src/app/layout.tsx**: Root layout with global providers
- **src/app/page.tsx**: Landing page
- **src/app/auth/**: Authentication pages (login, register)
- **src/app/dashboard/**: Dashboard pages
- **src/components/**: Reusable React components
- **src/lib/api/**: API client and endpoint methods
- **src/lib/utils/**: Utility functions
- **src/types/**: TypeScript type definitions
- **src/styles/globals.css**: Global styles and Tailwind directives

### Configuration

- **docker-compose.yml**: Local development environment orchestration
- **backend/Dockerfile**: Backend container definition
- **frontend/Dockerfile**: Frontend container definition (multi-stage)
- **backend/alembic.ini**: Database migration configuration
- **frontend/next.config.js**: Next.js configuration
- **frontend/tailwind.config.ts**: Tailwind CSS theme configuration

### Scripts

- **scripts/setup.sh**: One-command setup for new developers
- **scripts/dev.sh**: Development helper with common commands

## Technology Stack Summary

### Backend
- FastAPI (web framework)
- SQLAlchemy (ORM)
- Alembic (migrations)
- Pydantic v2 (validation)
- python-jose (JWT)
- passlib (password hashing)
- Anthropic SDK (Claude API)
- PostgreSQL driver (psycopg2)

### Frontend
- Next.js 14 (React framework)
- TypeScript (type safety)
- Tailwind CSS (styling)
- React Hook Form (forms)
- Zod (validation)
- Axios (HTTP client)

### Infrastructure
- Docker & Docker Compose
- PostgreSQL 15
- Node.js 18
- Python 3.11

## Next Steps After Setup

1. **Backend Development**:
   - Implement file upload handling
   - Complete WordPress scanner logic
   - Integrate Claude API for analysis
   - Add background job processing
   - Implement email verification

2. **Frontend Development**:
   - Build sites management pages
   - Create scan creation flow
   - Build scan results display
   - Add real-time scan status updates
   - Implement user profile management

3. **Testing**:
   - Write backend unit tests
   - Write backend integration tests
   - Write frontend component tests
   - Add E2E tests

4. **DevOps**:
   - Set up CI/CD pipeline
   - Configure production deployment
   - Add monitoring and logging
   - Implement backup strategy

## Development Workflow

1. Start development environment: `./scripts/setup.sh` (first time) or `./scripts/dev.sh start`
2. Make changes to code (hot reload enabled)
3. Create database migrations when needed: `./scripts/dev.sh migration "description"`
4. Run tests: `./scripts/dev.sh test backend` or `./scripts/dev.sh test frontend`
5. View logs: `./scripts/dev.sh logs`
6. Access interactive API docs at http://localhost:8000/docs

## File Count Summary

- Backend Python files: 20+
- Frontend TypeScript/TSX files: 15+
- Configuration files: 10+
- Documentation files: 4
- Docker files: 3
- Scripts: 2

Total: 50+ files created
