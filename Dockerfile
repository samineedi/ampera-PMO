# Stage 1: build the React app
FROM node:20-slim AS frontend
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Flask app serving the API and frontend/dist
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PORT=5000
WORKDIR /app

# Editable install: pmo.config finds the repo root (.env, data/, frontend/dist) from its own file location.
COPY backend/pyproject.toml backend/pyproject.toml
COPY backend/src backend/src
RUN pip install --no-cache-dir -e backend
COPY --from=frontend /build/dist frontend/dist

RUN useradd --create-home app && mkdir -p data && chown -R app:app data
USER app

VOLUME /app/data
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
    CMD python -c "import os,urllib.request as u; u.urlopen('http://localhost:%s/ping' % os.environ['PORT'])"

CMD ["python", "-m", "pmo"]
