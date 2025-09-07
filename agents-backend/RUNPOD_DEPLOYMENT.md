# RunPod Deployment Guide

This guide helps you deploy the Intelligent Ambience system to RunPod for GPU-accelerated music generation.

## Prerequisites

1. **RunPod Account**: Sign up at [runpod.io](https://runpod.io)
2. **RunPod CLI**: Install with `pip install runpod`
3. **API Key**: Get your API key from RunPod dashboard

## Quick Start

### 1. Login to RunPod
```bash
runpod login
# Enter your API key when prompted
```

### 2. Deploy the System
```bash
python deploy_runpod.py
```

### 3. Manual Deployment (Alternative)
```bash
# Build the pod
runpod build --name intelligent-ambience --config runpod_config.json

# Deploy the pod
runpod deploy --name intelligent-ambience
```

## Configuration

The system is configured for:
- **GPU**: RTX 4090, RTX 3090, A100, or A6000
- **Memory**: Minimum 8GB GPU memory
- **Storage**: 50GB container disk
- **Timeout**: 5 minutes startup, 10 minutes idle

## Usage

### Via RunPod Web Interface
1. Go to your RunPod dashboard
2. Find your deployed pod
3. Click "Connect" to open the web interface
4. Use the test endpoint with JSON payload:

```json
{
  "input": {
    "query": "Sarajevo, Bosnia and Herzegovina",
    "img_url": "https://example.com/image.jpg",
    "user_feedback": ""
  }
}
```

### Via API
```bash
curl -X POST "https://your-pod-id-8000.proxy.runpod.net/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Sarajevo, Bosnia and Herzegovina",
    "img_url": "https://example.com/image.jpg"
  }'
```

## File Structure

```
├── Dockerfile              # GPU-enabled container
├── runpod_handler.py       # RunPod serverless handler
├── runpod_config.json      # RunPod configuration
├── deploy_runpod.py        # Deployment script
├── main_graph.py           # Main system logic
└── requirements.txt        # Python dependencies
```

## Monitoring

- **Logs**: Check RunPod dashboard for real-time logs
- **GPU Usage**: Monitor GPU utilization in RunPod interface
- **Costs**: Track usage and costs in RunPod billing

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   - Reduce batch size in music generation
   - Use smaller models
   - Increase GPU memory allocation

2. **Model Loading Timeout**
   - Increase startup timeout in config
   - Pre-load models in container

3. **API Timeout**
   - Increase idle timeout
   - Optimize model inference speed

### Debug Mode
```bash
# Test locally before deployment
python runpod_handler.py
```

## Cost Optimization

- **Spot Instances**: Use spot pricing for lower costs
- **Auto-scaling**: Configure based on demand
- **Model Caching**: Cache models to reduce startup time
- **Batch Processing**: Process multiple requests together

## Security

- **API Keys**: Store securely in RunPod environment variables
- **Network**: Use RunPod's built-in security features
- **Data**: Ensure no sensitive data in logs

## Support

- **RunPod Docs**: [docs.runpod.io](https://docs.runpod.io)
- **Community**: RunPod Discord server
- **Issues**: Check RunPod status page
