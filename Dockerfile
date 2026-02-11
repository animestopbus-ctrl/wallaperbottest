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

# Set working directory
WORKDIR /app

# Install system dependencies with non-interactive frontend
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    curl \
    git \
    unzip \
    libjpeg-dev \
    libpng-dev \
    netcat \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r botuser && \
    useradd -r -g botuser botuser

# Copy requirements first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create required directories
RUN mkdir -p logs data && \
    chown -R botuser:botuser /app/logs /app/data

# Set permissions
RUN chown -R botuser:botuser /app /app/logs /app/data

# Switch to non-root user
USER botuser

# Health check command
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; print('OK'); sys.exit(0)"

# Default command
CMD ["python", "app.py"]

# Labels for metadata
LABEL maintainer="LastPerson07Bot" \
      version="2.0.0" \
      description="Premium Wallpaper Fetching Telegram Bot" \
      org.opencontainers.image.source="https://github.com/animestopbus-ctrl/wallpaperbottest"

# Expose port for health checks
EXPOSE 8000

# Create volumes
VOLUME ["/app/logs", "/app/data"]
