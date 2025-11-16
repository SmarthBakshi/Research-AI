#!/bin/bash
# Setup script to pull the LLM model in Ollama

set -e

echo "🚀 Setting up Ollama with llama3.2 model..."

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama service to be ready..."
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    echo "Waiting for Ollama..."
    sleep 5
done

echo "✅ Ollama is ready!"

# Pull the model
echo "📥 Pulling llama3.2 model (this may take several minutes)..."
docker exec researchai-ollama ollama pull llama3.2

echo "✅ Model pulled successfully!"
echo "🎉 Ollama setup complete! You can now use the /ask endpoint."
