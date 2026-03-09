# ── Stage 1: Builder ────────────────────────────────────────────
FROM python:3.11-slim-bookworm AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .
RUN grep -v 'boxlite' requirements.txt > requirements-docker.txt && \
    pip install --no-cache-dir --prefix=/install -r requirements-docker.txt

# ── Stage 2: Frontend builder ──────────────────────────────────
FROM node:22-alpine AS frontend-builder

WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# ── Stage 3: Runtime ───────────────────────────────────────────
FROM python:3.11-slim-bookworm AS runtime

LABEL org.opencontainers.image.source="https://github.com/ai-native-agentic/ClawWork" \
      org.opencontainers.image.title="ClawWork" \
      org.opencontainers.image.description="AI agent economic value measurement - LiveBench" \
      org.opencontainers.image.licenses="MIT"

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1000 clawwork && \
    useradd --uid 1000 --gid clawwork --shell /bin/bash --create-home clawwork

WORKDIR /app

COPY --from=builder /install /usr/local

COPY --chown=clawwork:clawwork livebench/ ./livebench/
COPY --chown=clawwork:clawwork scripts/ ./scripts/
COPY --chown=clawwork:clawwork setup.py ./
COPY --chown=clawwork:clawwork requirements.txt ./

COPY --from=frontend-builder --chown=clawwork:clawwork /frontend/dist ./frontend/dist

RUN mkdir -p /app/livebench/data /app/logs && \
    chown -R clawwork:clawwork /app/livebench/data /app/logs

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    LIVEBENCH_HTTP_PORT=8000

USER clawwork

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -sf http://127.0.0.1:8000/ || exit 1

CMD ["python", "-m", "uvicorn", "livebench.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
