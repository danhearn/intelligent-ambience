#!/bin/bash

# Startup script for RunPod deployment
echo "🚀 Starting Intelligent Ambience System..."

# Start Ollama service in background
echo "📦 Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to start
echo "⏳ Waiting for Ollama to start..."
sleep 10

# Pull the required model
echo "📥 Pulling Ollama model: gpt-oss:20b"
ollama pull gpt-oss:20b

# Verify model is available
echo "✅ Verifying model availability..."
ollama list

# Start the Python application
echo "🎵 Starting Intelligent Ambience API..."
python api_server.py

# Cleanup on exit
trap "kill $OLLAMA_PID" EXIT
