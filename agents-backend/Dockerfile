FROM nvidia/cuda:11.8-devel-ubuntu20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV CUDA_VISIBLE_DEVICES=0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3-pip \
    ffmpeg \
    libsndfile1 \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create symlink for python
RUN ln -s /usr/bin/python3.10 /usr/bin/python

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Set up Ollama environment
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_ORIGINS=*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for models and outputs
RUN mkdir -p generated_tracks chroma_langchain_db

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Make startup script executable
RUN chmod +x startup.sh

# Run the startup script
CMD ["./startup.sh"]
