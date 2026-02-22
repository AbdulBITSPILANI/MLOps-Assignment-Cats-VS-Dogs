FROM python:3.9-slim

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy project files
COPY src/ ./src/
COPY config.json .

# 🔴 IMPORTANT: copy trained model into image
COPY models/best_model.pth ./models/best_model.pth

# Create directories (safety)
RUN mkdir -p data/processed models

EXPOSE 8000

ENV PYTHONPATH=/app

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.inference.app:app", "--host", "0.0.0.0", "--port", "8000"]