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
# FIX: Set execute permissions for entrypoint.sh in the builder stage
RUN chmod +x /app/entrypoint.sh
RUN /opt/venv/bin/python -m compileall .

# ────────────────
# Stage 2: runtime
# ────────────────
FROM python:3.12-slim AS runtime
WORKDIR /app

# Create a dedicated non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser -s /sbin/nologin appuser

# Runtime-only tools we still need
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Bring in the venv and code from the builder
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

# Set permissions for venv, app directory, and logs directory for the non-root user
RUN chown -R appuser:appuser /opt/venv \
    && chown -R appuser:appuser /app \
    && mkdir -p /app/logs && chown appuser:appuser /app/logs

# Set the PATH for the non-root user (important for python and other venv executables)
ENV PATH="/opt/venv/bin:$PATH"

# Switch to the non-root user
USER appuser

# Entrypoint is already executable from the builder stage, and copied over
# No need for an extra COPY or chmod here
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "90"]

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f -H "Host: api.mushfiqurrahmanrobin.com" http://localhost:8000/health/ || exit 1
