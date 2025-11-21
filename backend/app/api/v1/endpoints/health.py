"""
Health Check Endpoint
Provides comprehensive health status for monitoring and orchestration
"""
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Dict, Any
import time

from app.db.session import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/health", tags=["health"])
def health_check(db: Session = Depends(get_db)) -> JSONResponse:
    """
    Comprehensive health check endpoint

    Checks:
    - API responsiveness
    - Database connectivity
    - Application configuration

    Returns:
    - 200: All systems operational
    - 503: Service unavailable (database issues)
    """
    health_status: Dict[str, Any] = {
        "status": "healthy",
        "service": "coderenew-api",
        "version": settings.VERSION,
        "timestamp": int(time.time()),
        "checks": {}
    }

    # Check database connectivity
    try:
        start_time = time.time()
        result = db.execute(text("SELECT 1"))
        result.scalar()
        db_latency = (time.time() - start_time) * 1000  # Convert to ms

        health_status["checks"]["database"] = {
            "status": "healthy",
            "latency_ms": round(db_latency, 2),
            "type": "postgresql"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e),
            "type": "postgresql"
        }

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )

    # Check configuration
    health_status["checks"]["configuration"] = {
        "status": "healthy",
        "debug_mode": settings.DEBUG,
        "environment": "production" if not settings.DEBUG else "development"
    }

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=health_status
    )


@router.get("/health/liveness", tags=["health"])
def liveness_check() -> JSONResponse:
    """
    Kubernetes liveness probe endpoint

    Simple check that the application is running
    Used by orchestrators to determine if the container should be restarted
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "alive",
            "service": "coderenew-api"
        }
    )


@router.get("/health/readiness", tags=["health"])
def readiness_check(db: Session = Depends(get_db)) -> JSONResponse:
    """
    Kubernetes readiness probe endpoint

    Checks if the application is ready to receive traffic
    Used by orchestrators to determine if the container should receive requests
    """
    try:
        # Check database connectivity
        db.execute(text("SELECT 1"))

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "ready",
                "service": "coderenew-api"
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "service": "coderenew-api",
                "reason": "database_unavailable",
                "error": str(e)
            }
        )
