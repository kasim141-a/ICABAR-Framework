# ICABAR Framework Dockerfile
# Multi-stage build for optimized production image

# Build stage
FROM python:3.8-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION
ARG VCS_REF

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Production stage
FROM python:3.8-slim as production

# Set labels for metadata
LABEL maintainer="ICABAR Framework Team" \
      org.opencontainers.image.title="ICABAR Framework" \
      org.opencontainers.image.description="Enhanced Recommender Systems through User Behaviour Analytics and Context-Aware Suggestions" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.source="https://github.com/yourusername/icabar-framework" \
      org.opencontainers.image.documentation="https://github.com/yourusername/icabar-framework/blob/main/README.md" \
      org.opencontainers.image.licenses="MIT"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO \
    WORKERS=4 \
    PORT=8000 \
    METRICS_PORT=8080

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r icabar && useradd -r -g icabar icabar

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create application directory
WORKDIR /app

# Copy application code
COPY --chown=icabar:icabar . .

# Create necessary directories
RUN mkdir -p /app/logs /app/cache /app/data && \
    chown -R icabar:icabar /app

# Switch to non-root user
USER icabar

# Expose ports
EXPOSE $PORT $METRICS_PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Default command
CMD ["python", "-m", "icabar_framework.main"]
