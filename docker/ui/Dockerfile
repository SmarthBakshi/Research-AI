FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with compatible versions
RUN pip install --no-cache-dir \
    gradio==4.16.0 \
    httpx==0.26.0 \
    huggingface-hub==0.20.0

# Copy application
COPY app.py /app/

# Expose port
EXPOSE 7860

# Run the application
CMD ["python", "app.py"]
