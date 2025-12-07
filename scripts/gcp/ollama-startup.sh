#!/bin/bash
# Ollama GPU Setup Script for GCP Compute Engine
# This runs automatically when the VM starts

set -e

echo "🚀 Starting Ollama GPU setup..."

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Install NVIDIA Container Toolkit
if ! dpkg -l | grep -q nvidia-container-toolkit; then
    echo "🔧 Installing NVIDIA Container Toolkit..."
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | apt-key add -
    curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    apt-get update
    apt-get install -y nvidia-container-toolkit
    systemctl restart docker
fi

# Stop existing Ollama container if running
docker stop ollama 2>/dev/null || true
docker rm ollama 2>/dev/null || true

# Run Ollama with GPU support
echo "🐳 Starting Ollama container with GPU..."
docker run -d \
  --gpus all \
  --name ollama \
  -p 11434:11434 \
  --restart unless-stopped \
  -v ollama-data:/root/.ollama \
  ollama/ollama

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to start..."
sleep 10

# Pull llama3.2 model
echo "📥 Pulling llama3.2 model (this takes 2-3 minutes)..."
docker exec ollama ollama pull llama3.2

echo "✅ Ollama GPU setup complete!"
echo "🔍 Test with: docker exec ollama ollama run llama3.2 'Say hello'"
