#!/bin/bash

# Initialize Ollama models for local development
echo "🤖 Initializing Ollama models..."

# Wait for Ollama to be ready
echo "Waiting for Ollama to be ready..."
until curl -f http://localhost:11434/api/tags > /dev/null 2>&1; do
  echo "Waiting for Ollama..."
  sleep 5
done

echo "Ollama is ready! Pulling models..."

# Pull the chat model
echo "Pulling phi3:mini (3.8B parameters)..."
ollama pull phi3:mini

# Pull the embedding model
echo "Pulling nomic-embed-text (137M parameters)..."
ollama pull nomic-embed-text

echo "✅ Models initialized successfully!"
echo "Available models:"
ollama list
