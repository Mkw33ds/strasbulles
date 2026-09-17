FROM node:22-alpine AS assets
WORKDIR /build
COPY package.json package-lock.json* ./
RUN npm install --no-audit --no-fund
COPY static_src ./static_src
RUN mkdir -p static/css && npm run css:build

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN addgroup --gid 1000 django && adduser --uid 1000 --gid 1000 --disabled-password --gecos "" django
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY --from=assets /build/static/css/site.css ./static/css/site.css
COPY . .
RUN mkdir -p /app/media /app/staticfiles
RUN chown -R django:django /app
USER django
ENTRYPOINT ["sh", "/app/docker/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind=0.0.0.0:8000", "--workers=3", "--timeout=90", "--access-logfile=-", "--error-logfile=-"]

FROM runtime AS development
USER root
COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
USER django

FROM runtime AS production
