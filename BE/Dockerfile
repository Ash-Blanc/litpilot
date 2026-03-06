FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project definition
COPY pyproject.toml ./

# Install dependencies (ignoring missing packages for now, just caching)
RUN uv pip install -r pyproject.toml --system || true

# Copy source
COPY . .

# Install correctly with source
RUN uv pip install -e . --system

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7777"]
