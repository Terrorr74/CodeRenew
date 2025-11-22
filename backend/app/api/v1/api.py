"""
API Router
Combines all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, sites, scans, orders, health, webhooks

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(sites.router, prefix="/sites", tags=["sites"])
api_router.include_router(scans.router, prefix="/scans", tags=["scans"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
