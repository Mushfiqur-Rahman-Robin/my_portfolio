# Use the official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN uv pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# The command to run the application
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]