# Multi-stage build for pond planner application
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential=12.9 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and use a non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install runtime dependencies and security updates
RUN apt-get update && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and use a non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Set work directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser . .

# Remove development files
RUN rm -rf tests/ \
    requirements-dev.txt \
    pytest.ini \
    .trunk/ \
    .git* \
    README.md

# Create directory for any runtime data
RUN mkdir -p /app/data && chown appuser:appuser /app/data

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from PondPlanner import PondPlanner; p = PondPlanner(); print('OK')" || exit 1

# Expose port (if needed for future web interface)
EXPOSE 8000

# Default command
ENTRYPOINT ["python"]
CMD ["main.py"]

# Labels for metadata
LABEL org.opencontainers.image.title="Pond Planner"
LABEL org.opencontainers.image.description="A comprehensive pond planning application for calculating pond dimensions, fish stocking, and equipment requirements"
LABEL org.opencontainers.image.source="https://github.com/parttimelegend/pond-planner"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.vendor="Pond Planner"
