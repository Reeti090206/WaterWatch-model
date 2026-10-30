# WaterWatch AI Backend Dockerfile
FROM python:3.11-slim

# Install system dependencies for OpenCV and graphics utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install CPU-optimized PyTorch and dependencies
COPY requirements-backend.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements-backend.txt

# Copy application source code and models
COPY . /app/

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production
ENV INTEGRATION_HOST=0.0.0.0
ENV INTEGRATION_PORT=8080

EXPOSE 8080

CMD ["python", "waterwatch_integration/run_integration.py"]

