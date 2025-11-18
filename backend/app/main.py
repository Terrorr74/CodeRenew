"""
CodeRenew FastAPI Application
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1.api import api_router
from app.db.session import engine
from app.models import base  # Import all models for Alembic

# Create database tables (in production, use Alembic migrations)
# base.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="WordPress compatibility scanner and analysis tool",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"Documentation available at: /docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    print(f"Shutting down {settings.PROJECT_NAME}")
