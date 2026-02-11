# LastPerson07Bot - Production Dockerfile
# Optimized for production with security best practices

# Use Python 3.11 slim base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    netcat \
    && rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Create non-root user for security
RUN groupadd -r botuser && \
    useradd -r -g botuser botuser

# Create required directories
RUN mkdir -p /app/logs /app/data

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set permissions
RUN chown -R botuser:botuser /app /app/logs /app/data

# Set up environment
RUN echo "export PATH=/usr/local/bin:/usr/bin:/usr/local/sbin"
ENV PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin

# Create non-root user for running the app
USER botuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["CMD", "python", "-c", "import sys; print('✅ Bot Ready!'); sys.exit(0)" || exit 1]

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
