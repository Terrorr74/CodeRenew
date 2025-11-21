# syntax=docker/dockerfile:1

# ============================================
# Stage 1: Builder - Install dependencies
# ============================================
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies required for Python packages
# gcc: Required for compiling Python packages with C extensions
# build-essential: Provides additional build tools
# libpq-dev: PostgreSQL client library headers for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment to isolate dependencies
RUN python -m venv /opt/venv

# Activate virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies
# Copying requirements.txt separately enables Docker layer caching
# Dependencies will only reinstall if requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 2: Runtime - Production image
# ============================================
FROM python:3.11-slim AS runtime

# Set working directory
WORKDIR /app

# Install only runtime dependencies (no build tools)
# postgresql-client: Required for database operations and health checks
# curl: Required for Docker HEALTHCHECK
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Activate virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
# Running as non-root reduces attack surface
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create necessary directories and set ownership
RUN mkdir -p /app/uploads && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 8000

# Configure health check
# Checks if the application is responding to HTTP requests
# start-period: Gives app time to start (including DB migrations)
# interval: Check every 30 seconds
# timeout: Wait up to 10 seconds for response
# retries: Mark unhealthy after 3 consecutive failures
HEALTHCHECK --start-period=40s --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run the application
# --host 0.0.0.0: Listen on all network interfaces
# --port 8000: Application port
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
