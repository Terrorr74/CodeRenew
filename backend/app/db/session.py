"""
Database session management
SQLAlchemy engine and session configuration with production-ready connection pooling
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator

from app.core.config import settings

# Production-ready connection pool configuration
# Connection pool settings explained:
# - pool_size: Number of connections to keep open in the pool (5 is recommended for most apps)
# - max_overflow: Maximum number of connections that can be created beyond pool_size (10 recommended)
# - pool_pre_ping: Test connection liveness before using (prevents "connection lost" errors)
# - pool_recycle: Recycle connections after 3600 seconds (1 hour) to prevent stale connections
# - pool_timeout: Seconds to wait before giving up on getting a connection from pool
# - pool_use_lifo: Use LIFO (Last In First Out) for connection retrieval
#
# Total max connections = pool_size + max_overflow = 5 + 10 = 15
# This should be well below PostgreSQL's max_connections setting (typically 100)
#
# For production, ensure PostgreSQL max_connections is set appropriately:
# max_connections = (pool_size + max_overflow) * number_of_app_instances + buffer
# Example: (5 + 10) * 3 instances + 20 buffer = 65 connections minimum

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,              # Persistent connections in pool
    max_overflow=10,          # Additional connections allowed
    pool_pre_ping=True,       # Verify connections before use
    pool_recycle=3600,        # Recycle connections after 1 hour
    pool_timeout=30,          # Wait up to 30 seconds for a connection
    pool_use_lifo=True,       # LIFO allows server to close idle connections
    echo=settings.DEBUG,      # Log SQL queries in debug mode
    echo_pool=settings.DEBUG, # Log connection pool events in debug mode
)

# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session
    Use with FastAPI Depends()

    Yields:
        Database session

    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
