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

# Create and set up the entrypoint script directly in the Dockerfile
RUN echo '#!/bin/bash\n\
echo "Waiting for PostgreSQL..."\n\
while ! nc -z db 5432; do\n\
    sleep 0.1\n\
done\n\
echo "PostgreSQL started"\n\
\n\
echo "Running migrations..."\n\
python manage.py migrate\n\
\n\
echo "Starting server..."\n\
python manage.py runserver 0.0.0.0:8000' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

# Copy project
COPY . .

# Set entrypoint
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]