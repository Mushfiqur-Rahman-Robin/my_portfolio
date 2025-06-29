# multi stage image build

# ────────────────
# Stage 1: builder
# ────────────────
FROM python:3.12-slim AS builder
WORKDIR /app

# Tools needed at *build* time
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

COPY requirements.txt .
RUN uv venv /opt/venv
RUN uv pip install --python /opt/venv/bin/python --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/logs && chmod -R 777 /app/logs
RUN /opt/venv/bin/python manage.py collectstatic --noinput
RUN /opt/venv/bin/python -m compileall .

# ────────────────
# Stage 2: runtime
# ────────────────
FROM python:3.12-slim AS runtime
WORKDIR /app

# Runtime-only tools we still need
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl postgresql-client \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Bring in the venv and code from the builder
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

# Entrypoint
COPY entrypoint.sh .
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "90"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f -H "Host: api.mushfiqurrahmanrobin.com" http://localhost:8000/health/ || exit 1
