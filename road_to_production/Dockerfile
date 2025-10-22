# VideoMusic Generator - Production Docker Image
# Multi-stage build for optimized image size

FROM python:3.11-slim as base

# Metadata
LABEL maintainer="VideoMusic Generator"
LABEL description="AI-powered music video generator with Suno, Replicate, and OpenAI"
LABEL version="1.0.0"

# Install system dependencies including FFmpeg and ImageMagick
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configure ImageMagick policy to allow video processing
RUN sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml || true

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements-prod.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY web/ ./web/
COPY web_app_secure.py .
COPY database.py .
COPY api_validator.py .

# Create necessary directories with proper permissions
RUN mkdir -p /app/output /app/data && \
    chmod -R 755 /app/output /app/data

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "web_app_secure.py"]
