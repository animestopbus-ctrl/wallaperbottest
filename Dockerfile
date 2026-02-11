# LastPerson07Bot - Simpler Dockerfile
# Works without complex graphics dependencies

# Use Python 3.11 slim base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    && rm -rf /var/lib/apt/lists/* && apt-get clean

# Create non-root user for security
RUN groupadd -r botuser && \
    useradd -r -g botuser botuser

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create required directories
RUN mkdir -p logs data

# Set permissions
RUN chown -R botuser:botuser /app /app/logs /app/data

# Switch to non-root user
USER botuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; print('OK'); sys.exit(0)" || exit 1

# Default command
CMD ["python", "app.py"]

# Labels for metadata
LABEL maintainer="LastPerson07Bot" \
      version="2.0.0" \
      description="Premium Wallpaper Fetching Telegram Bot" \
      org.opencontainers.image.source="https://github.com/animestopbus-ctrl/wallpaperbottest" \
      org.opencontainers.image.licenses="MIT"

# Expose port for health checks
EXPOSE 8000

# Create volumes
VOLUME ["/app/logs", "/app/data"]
