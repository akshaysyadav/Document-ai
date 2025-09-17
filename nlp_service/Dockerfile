# Multi-stage build for better caching and optimization
FROM python:3.10-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies in a single layer
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create cache directory for Hugging Face models
RUN mkdir -p /app/.cache /app/models
ENV TRANSFORMERS_CACHE=/app/models
ENV HF_HOME=/app/models
ENV TORCH_HOME=/app/models

# Dependencies stage
FROM base as dependencies

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Model download stage - This ensures models are ALWAYS in the image
FROM dependencies as model_downloader

# Copy the download script
COPY download_model.py .

# Download models during build - This happens ONCE per image build
RUN python download_model.py && \
    echo "✅ Models permanently cached in image at /app/models"

# Final stage
FROM dependencies as final

# Copy pre-downloaded models from previous stage
COPY --from=model_downloader /app/models /app/models

# Copy application code
COPY app.py .

# Ensure models directory is properly set
ENV TRANSFORMERS_CACHE=/app/models
ENV HF_HOME=/app/models
ENV TORCH_HOME=/app/models

# Create a marker file to indicate models are pre-installed
RUN echo "Models pre-installed in Docker image" > /app/models/.models_ready

# Expose port
EXPOSE 8000

# Health check with longer timeout for large model
HEALTHCHECK --interval=60s --timeout=45s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"] 