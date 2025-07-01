# 🐳 DocSync - Enterprise Docker Image
# Multi-stage build for optimized production image

# Stage 1: Build Dependencies
FROM python:3.11-slim-bullseye AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r docsync && useradd -r -g docsync docsync

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install build && \
    python -m build && \
    pip install dist/*.whl && \
    rm -rf dist/ build/ src/

# Stage 2: Production Image
FROM python:3.11-slim-bullseye AS production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DOCSYNC_ENV=production \
    DOCSYNC_LOG_LEVEL=INFO

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r docsync && useradd -r -g docsync docsync

# Set working directory
WORKDIR /app

# Copy from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/docsync /usr/local/bin/docsync

# Create necessary directories
RUN mkdir -p /app/data /app/config /app/logs && \
    chown -R docsync:docsync /app

# Copy configuration templates
COPY --chown=docsync:docsync templates/ /app/templates/
COPY --chown=docsync:docsync examples/ /app/examples/

# Switch to non-root user
USER docsync

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD docsync --version || exit 1

# Expose port (if web interface is added)
EXPOSE 8000

# Set default command
CMD ["docsync", "--help"]

# Labels for metadata
LABEL maintainer="NEO-SH1W4" \
      description="Advanced technical documentation synchronization system" \
      version="0.1.0" \
      org.opencontainers.image.source="https://github.com/NEO-SH1W4/docsync" \
      org.opencontainers.image.documentation="https://github.com/NEO-SH1W4/docsync#readme" \
      org.opencontainers.image.licenses="MIT"

