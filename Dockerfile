# LastPerson07Bot - Production Dockerfile
# Minimal dependencies for reliable builds

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install minimal system dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    netcat \
    && rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create app user
RUN groupadd -r botuser && \
    useradd -r -g botuser botuser

# Create required directories
RUN mkdir -p /app/logs /app/data

# Copy application code
COPY . .

# Set permissions
RUN chown -R botuser:botuser /app /app/logs /app/data

# Switch to non-root user
USER botuser

# Environment setup
ENV PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin
ENV PYTHONPATH=/usr/local/bin

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; print('Bot ready!'); sys.exit(0)" || exit 1

# Default command
CMD ["python", "app.py"]

# Labels
LABEL maintainer="LastPerson07Bot" \
      version="2.0.0" \
      description="Premium Wallpaper Fetching Telegram Bot" \
      org.opencontainers.image.source="https://github.com/animestopbus-ctrl/wallpaperbottest" \
      org.opencontainers.image.licenses="MIT"

# Expose port for health checks
EXPOSE 8000

# Create volumes
VOLUME ["/app/logs", "/app/data"]

# Set working directory
WORKDIR /app
