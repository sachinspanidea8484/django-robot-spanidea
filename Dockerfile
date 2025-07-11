FROM python:3.11-slim-bullseye AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    # Add any other system dependencies needed by Robot Framework
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:$PYTHONPATH

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files (for production builds)
COPY robot_framework_runner /app/robot_framework_runner
COPY robot-framework-automation /app/robot-framework-automation

# Create necessary directories
RUN mkdir -p /app/outputs && \
    mkdir -p /app/robot_framework_runner/logs

# Set proper permissions
RUN chmod -R 755 /app

# Expose port
EXPOSE 8080

# Change to Django project directory
WORKDIR /app/robot_framework_runner

# Default command (can be overridden by docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]