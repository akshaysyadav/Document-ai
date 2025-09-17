# KMRL NLP Service

Advanced NLP service using Google's Flan-T5-Large model for document processing tasks.

## Features

- **Document Summarization**: Generate concise bullet-point summaries
- **Key Highlight Extraction**: Identify important sections and ideas
- **Task Extraction**: Find actionable items and tasks
- **High-Quality AI**: Powered by Google's Flan-T5-Large model

## API Endpoints

### POST /summarize
Generate document summary in bullet points.

**Request:**
```json
{
  "text": "Your document text here..."
}
```

**Response:**
```json
{
  "summary": [
    "First key point from the document",
    "Second important insight",
    "Third main finding"
  ],
  "method": "flan-t5-large"
}
```

### POST /highlight
Extract key highlights and important sections.

**Request:**
```json
{
  "text": "Your document text here..."
}
```

**Response:**
```json
{
  "highlights": [
    "Most important section identified",
    "Key decision or finding",
    "Critical information highlighted"
  ],
  "method": "flan-t5-large"
}
```

### POST /tasks
Extract actionable tasks and action items.

**Request:**
```json
{
  "text": "Your document text here..."
}
```

**Response:**
```json
{
  "tasks": [
    {
      "text": "Review the quarterly report",
      "priority": "high",
      "status": "open"
    },
    {
      "text": "Schedule team meeting",
      "priority": "medium", 
      "status": "open"
    }
  ],
  "method": "flan-t5-large"
}
```

### GET /health
Check service health and model status.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cpu"
}
```

## System Requirements

- **Memory**: 4GB+ RAM (2GB minimum)
- **CPU**: Multi-core recommended
- **GPU**: Optional (CUDA support)
- **Storage**: ~3GB for model weights

## Docker Usage

### Using docker-compose (Recommended)

```bash
# Start all services including NLP
docker-compose up

# Start only NLP service
docker-compose up nlp_service

# Check logs
docker-compose logs nlp_service
```

### Standalone Docker

```bash
# Build the image
cd nlp_service
docker build -t kmrl-nlp-service .

# Run the container
docker run -p 8001:8000 \
  -v nlp_cache:/app/.cache \
  --memory=4g \
  kmrl-nlp-service
```

## Testing

```bash
# Run the test script
python test_nlp_service.py

# Manual testing
curl -X POST http://localhost:8001/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Your test document here..."}'
```

## Model Information

- **Model**: google/flan-t5-large
- **Size**: ~3GB
- **Type**: Text-to-Text Transfer Transformer
- **Capabilities**: Summarization, Question Answering, Text Generation
- **License**: Apache 2.0

## Performance Notes

- **First Request**: May take 30-60 seconds (model loading)
- **Subsequent Requests**: 5-15 seconds depending on text length
- **Memory Usage**: 2-4GB during inference
- **GPU Acceleration**: Automatically used if available

## Environment Variables

- `TRANSFORMERS_CACHE`: Cache directory for models (default: `/app/.cache`)
- `HF_HOME`: Hugging Face home directory
- `TORCH_HOME`: PyTorch cache directory

## Troubleshooting

### Model Loading Issues
- Ensure sufficient memory (4GB+)
- Check internet connection for model download
- Verify disk space for model cache

### Performance Issues
- Use GPU if available
- Increase memory allocation
- Reduce input text length (max 4000 chars)

### Connection Issues
- Verify service is running: `docker-compose ps`
- Check health endpoint: `curl http://localhost:8001/health`
- Review logs: `docker-compose logs nlp_service` 