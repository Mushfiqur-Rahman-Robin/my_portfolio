FROM python:3.12-slim

# Set environment variables to ensure Python outputs logs immediately
ENV PYTHONFAULTHANDLER=1
# Disable bytecode generation to save space
ENV PYTHONDONTWRITEBYTECODE=1
# Disable buffering of stdout and stderr to ensure logs are output immediately
ENV PYTHONUNBUFFERED=1

# Set the working directory to /app
WORKDIR /app

# Install runtime OS tools needed later (curl for HEALTHCHECK)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv's installation directory to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy requirements.txt to /app
COPY requirements.txt .

# Create virtual environment at /opt/venv (outside /app to avoid volume mount override)
RUN uv venv /opt/venv

# Install dependencies (ensure gunicorn is in requirements.txt!)
RUN uv pip install --python /opt/venv/bin/python --no-cache-dir -r requirements.txt

# Update PATH to include the virtual environment's bin directory
ENV PATH="/opt/venv/bin:$PATH"

# Copy the application code to /app
COPY . .

# Collect all static files into STATIC_ROOT
RUN python manage.py collectstatic --noinput

# Create a gunicorn configuration file
COPY gunicorn.conf.py .

# Copy entrypoint script and make it executable
COPY entrypoint.sh .
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# Use entrypoint.sh as the entrypoint, with CMD as the default argument
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "90"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/admin/ || exit 1
