FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Generate sample files
RUN python sample_data/create_samples.py

# Expose Web Server and Socket Server ports
EXPOSE 8000 9099

# Startup script to run both Socket Server and FastAPI Web Server concurrently
CMD python run_socket_server.py & uvicorn main:app --host 0.0.0.0 --port 8000
