# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-minimal.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=web_app.py

# Run the application
CMD ["python", "start_services.py"]