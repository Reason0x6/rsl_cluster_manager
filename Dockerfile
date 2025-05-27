FROM python:3.11-slim

# Install system dependencies
RUN apt-get update \
    && apt-get install -y netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set work directory and create it
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Create required directories
RUN mkdir -p /app/static /app/media

# Copy the entire project
COPY manage.py /app/
COPY raid_clan_manager /app/raid_clan_manager/
COPY clans /app/clans/
COPY docker/entrypoint.sh /app/entrypoint.sh

# Set proper permissions
RUN chmod +x /app/entrypoint.sh \
    && chown -R www-data:www-data /app

USER www-data

ENTRYPOINT ["/app/entrypoint.sh"]