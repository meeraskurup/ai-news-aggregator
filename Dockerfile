# AI News Aggregator Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for newspaper3k
RUN apt-get update && apt-get install -y \
    libxml2-dev \
    libxslt-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for SQLite database
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:///./data/news.db

# Expose port
EXPOSE 8000

# Default command - run the web server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
