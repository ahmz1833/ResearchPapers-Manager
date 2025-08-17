# Python slim base
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps (add curl for healthcheck) + security upgrades
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    build-essential netcat-traditional curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m appuser

WORKDIR /app

# Install dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Copy source
COPY app ./app
COPY scripts ./scripts
COPY wsgi.py ./

USER appuser

EXPOSE 8000

# Default environment variables (can be overridden by docker-compose env_file)
ENV APP_NAME=research-papers-manager \
    FLASK_ENV=production \
    MONGODB_URI=mongodb://mongo:27017 \
    MONGODB_DB=research_db \
    REDIS_URL=redis://redis:6379/0 \
    PORT=8000 \
    ENABLE_SCHEDULER=true \
    VIEWS_SYNC_INTERVAL_MIN=10

# Gunicorn config
ENV GUNICORN_CMD_ARGS="--bind 0.0.0.0:8000 --workers=4 --timeout 60 --graceful-timeout 30 --log-level=info"

CMD ["gunicorn", "wsgi:app"]
