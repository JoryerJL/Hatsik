# ==============================================================
# Hatsik — Production Dockerfile
# ==============================================================
# Python 3.12 slim + Tailwind CLI standalone + Gunicorn
# ==============================================================

FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/production.txt requirements/base.txt requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

# Download Tailwind CSS standalone binary (linux x64)
RUN curl -sLo /usr/local/bin/tailwindcss \
    https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64 \
    && chmod +x /usr/local/bin/tailwindcss

# Copy application code
COPY . .

# Compile Tailwind CSS (minified for production)
RUN tailwindcss -i static/css/input.css -o static/css/main.css --minify

# Collect static files (WhiteNoise serves them)
RUN python manage.py collectstatic --noinput --settings=config.settings.production || true

# Expose port
EXPOSE 8000

# Run with Gunicorn
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
