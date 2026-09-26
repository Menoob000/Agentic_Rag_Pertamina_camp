# ─────────────────────────────────────────
# Dapur AI (FastAPI + Python) Dockerfile
# V2 — OpenRouter + Qdrant Cloud
# ─────────────────────────────────────────
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files first (for better Docker caching)
COPY pyproject.toml ./

# Install dependencies
ENV UV_HTTP_TIMEOUT=600
RUN uv sync --no-dev

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/drafts /app/output /app/RAG/Data

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["uv", "run", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
