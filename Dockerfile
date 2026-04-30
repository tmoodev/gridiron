FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]" && playwright install chromium --with-deps

COPY . .

CMD ["uvicorn", "gridiron.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
