# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install netcat for database check
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set work directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh && \
    sed -i 's/\r$//g' /app/entrypoint.sh

# Copy project
COPY . .

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]