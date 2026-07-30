# Thai2Drive Backend — Railway Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Railway injects PORT at runtime; 8080 is only the local/offline default.
ENV PORT=8080

# Start FastAPI with uvicorn on the port Railway assigns.
# `sh -c` is required so ${PORT} expands — the exec form never expands variables.
# `exec` then replaces the shell with uvicorn so it runs as PID 1 and receives
# SIGTERM directly, preserving the graceful-shutdown fix from eb47c1f.
CMD ["sh", "-c", "exec uvicorn server:app --host 0.0.0.0 --port ${PORT:-8080}"]
