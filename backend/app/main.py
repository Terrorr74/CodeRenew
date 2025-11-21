"""
CodeRenew FastAPI Application
Main application entry point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.api.v1.api import api_router
from app.db.session import engine
from app.models import base  # Import all models for Alembic
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.core.rate_limiting import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    Replaces deprecated @app.on_event("startup") and @app.on_event("shutdown")
    """
    # Startup logic
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"Documentation available at: /docs")
    print(f"Security features enabled: Rate limiting, Account lockout, Password policy")

    yield

    # Shutdown logic
    print(f"Shutting down {settings.PROJECT_NAME}")


# Create database tables (in production, use Alembic migrations)
# base.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="WordPress compatibility scanner and analysis tool with enhanced security",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan  # Use lifespan instead of deprecated on_event decorators
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Configure rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "message": "CodeRenew API",
        "version": settings.VERSION,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "coderenew-api",
            "version": settings.VERSION
        }
    )


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)
