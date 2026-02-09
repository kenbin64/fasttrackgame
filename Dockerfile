# ButterflyFx Server - Production Dockerfile
# Multi-stage build for minimal image size

# Stage 1: Builder
FROM python:3.14-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY server/requirements.txt /app/server/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r server/requirements.txt

# Stage 2: Runtime
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 butterflyfx && \
    chown -R butterflyfx:butterflyfx /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=butterflyfx:butterflyfx kernel/ /app/kernel/
COPY --chown=butterflyfx:butterflyfx core/ /app/core/
COPY --chown=butterflyfx:butterflyfx server/ /app/server/
COPY --chown=butterflyfx:butterflyfx helpers/ /app/helpers/
COPY --chown=butterflyfx:butterflyfx structures/ /app/structures/
COPY --chown=butterflyfx:butterflyfx algorithms/ /app/algorithms/
COPY --chown=butterflyfx:butterflyfx patterns/ /app/patterns/

# Switch to non-root user
USER butterflyfx

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    WORKERS=4 \
    HOST=0.0.0.0 \
    PORT=8000 \
    LOG_LEVEL=info

# Run server with configurable workers
CMD uvicorn server.main:app \
    --host ${HOST} \
    --port ${PORT} \
    --workers ${WORKERS} \
    --log-level ${LOG_LEVEL} \
    --no-access-log

