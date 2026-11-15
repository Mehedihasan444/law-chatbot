# Bangladesh Constitution Chatbot - Docker image
# Serves the FastAPI REST API by default; can also run the Streamlit UI
# (see docker-compose.yml for both services).
FROM python:3.11-slim

# Build tools required by some Python packages (e.g. faiss-cpu, torch)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for better layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Pre-create directories so volume mounts have predictable targets
RUN mkdir -p data/raw data/processed vectorstore

# REST API listens on port 8000
EXPOSE 8000

# Default: run the API server (host/port already default to 0.0.0.0:8000)
CMD ["python", "api.py", "--host", "0.0.0.0", "--port", "8000"]
