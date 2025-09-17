# KMRL Document AI - Enhanced Processing Pipeline

This document describes the enhanced document processing pipeline that provides end-to-end PDF processing with advanced NLP capabilities.

## 🚀 Features

### Core Pipeline
- **PDF Text Extraction**: Multi-method PDF text extraction with OCR fallback
- **Intelligent Chunking**: Token-aware text chunking with configurable parameters
- **Vector Embeddings**: High-quality text embeddings using sentence-transformers
- **Entity Extraction**: Named Entity Recognition using spaCy
- **Task Detection**: Hybrid rule-based + LLM task extraction
- **Document Summarization**: Hierarchical summarization with multiple models
- **Vector Search**: Semantic search using Qdrant vector database

### Advanced Capabilities
- **Background Processing**: Asynchronous job processing with Redis + RQ
- **Multi-Model Support**: HuggingFace transformers with OpenAI fallbacks
- **Comprehensive Metadata**: Rich metadata storage and retrieval
- **Task Management**: Full CRUD operations for extracted tasks
- **Processing Reports**: Detailed analytics and processing statistics
- **Health Monitoring**: Comprehensive health checks for all services

## 🏗️ Architecture

### Services
- **PostgreSQL**: Primary database for metadata and document records
- **Redis**: Caching layer and job queue management
- **Qdrant**: Vector database for semantic search
- **MinIO**: Object storage for document files

### Processing Flow
```
Document Upload → PDF Extraction → Text Chunking → NLP Processing → Vector Storage → Summarization → Task Extraction → Results
```

## 📊 Data Models

### Enhanced Tables
- `chunks`: Text chunks with embeddings and NLP metadata
- `summaries`: Multi-level document summaries
- `tasks`: Extracted actionable tasks with metadata

### Key Fields
- **Chunks**: `embedding_id`, `nlp_metadata`, `status`
- **Tasks**: `assignee`, `due_date`, `priority`, `status`, `extracted_by`
- **Summaries**: `level`, `method`, `text`

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# Redis
REDIS_URL=redis://localhost:6379/0

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=optional_key

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_BUCKET=documents

# Models
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
SUMMARIZER_MODEL_NAME=facebook/bart-large-cnn
TASK_EXTRACTOR_MODEL=google/flan-t5-large

# OpenAI (Optional)
USE_OPENAI=false
OPENAI_API_KEY=your_key_here

# Chunking
CHUNK_SIZE_TOKENS=500
CHUNK_OVERLAP_TOKENS=50
```

## 🚀 Quick Start

### 1. Setup Development Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Setup services
python scripts/setup_dev.py

# Start services (Docker)
docker run -d -p 6379:6379 redis:7-alpine
docker run -d -p 6333:6333 qdrant/qdrant
docker run -d -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ':9001'
```

### 2. Run Database Migration
```bash
alembic upgrade head
```

### 3. Start Services
```bash
# Start API server
python -m app.main

# Start background workers (separate terminal)
python -m app.workers
```

### 4. Test Pipeline
```bash
python scripts/test_pipeline.py
```

## 📡 API Endpoints

### Document Management
- `POST /api/documents/` - Upload and create document
- `GET /api/documents/` - List documents with pagination
- `GET /api/documents/{id}` - Get document details
- `PUT /api/documents/{id}` - Update document
- `DELETE /api/documents/{id}` - Delete document

### Enhanced Pipeline
- `GET /api/documents/{id}/results` - Get comprehensive processing results
- `GET /api/documents/{id}/chunks` - Get document chunks
- `GET /api/documents/{id}/tasks` - Get extracted tasks
- `PATCH /api/documents/tasks/{id}` - Update task
- `POST /api/documents/{id}/reprocess` - Reprocess document
- `GET /api/documents/{id}/report` - Get processing report

### Health & Status
- `GET /health` - API health check
- `GET /api/status` - Service status
- `GET /api/documents/health` - Document service health

## 🔄 Processing Pipeline

### 1. Document Upload
```python
# Upload document
files = {"file": ("document.pdf", pdf_file, "application/pdf")}
data = {"title": "My Document", "description": "Test document"}
response = requests.post("/api/documents/", files=files, data=data)
doc_id = response.json()["id"]
```

### 2. Background Processing
The system automatically:
1. Downloads PDF from MinIO
2. Extracts text using multiple methods
3. Chunks text into manageable pieces
4. Generates embeddings for each chunk
5. Extracts entities and tasks
6. Creates hierarchical summaries
7. Stores results in database and vector DB

### 3. Retrieve Results
```python
# Get comprehensive results
response = requests.get(f"/api/documents/{doc_id}/results")
results = response.json()

print(f"Summary: {results['summary']}")
print(f"Tasks: {len(results['tasks'])}")
print(f"Chunks: {len(results['chunks'])}")
```

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/

# Run specific test files
pytest tests/test_end_to_end.py
pytest tests/test_services.py
pytest tests/test_workers.py
```

### Test Coverage
- **End-to-end tests**: Complete pipeline testing
- **Service tests**: Individual service functionality
- **Worker tests**: Background job processing
- **API tests**: REST endpoint functionality

## 📈 Monitoring & Observability

### Health Checks
- Database connectivity
- Redis availability
- Qdrant service status
- MinIO bucket access
- Model loading status

### Processing Metrics
- Document processing time
- Chunk creation statistics
- Task extraction accuracy
- Embedding generation performance
- Vector storage efficiency

### Logging
- Structured logging with different levels
- Processing trace IDs
- Error tracking and reporting
- Performance metrics

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection
```bash
# Check PostgreSQL connection
psql -h localhost -U kmrl_user -d kmrl_db -c "SELECT 1;"
```

#### 2. Redis Issues
```bash
# Check Redis
redis-cli ping
```

#### 3. Qdrant Problems
```bash
# Check Qdrant
curl http://localhost:6333/collections
```

#### 4. Model Loading
```bash
# Download spaCy model
python -m spacy download en_core_web_sm
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python -m app.main
```

## 🚀 Production Deployment

### Docker Compose
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: kmrl_db
      POSTGRES_USER: kmrl_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  qdrant:
    image: qdrant/qdrant:latest
    volumes:
      - qdrant_data:/qdrant/storage

  minio:
    image: minio/minio:latest
    environment:
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: secure_password
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"

  backend:
    build: .
    environment:
      - DATABASE_URL=postgresql://kmrl_user:secure_password@postgres:5432/kmrl_db
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_URL=http://qdrant:6333
      - MINIO_ENDPOINT=minio:9000
    depends_on:
      - postgres
      - redis
      - qdrant
      - minio

  worker:
    build: .
    command: python -m app.workers
    environment:
      - DATABASE_URL=postgresql://kmrl_user:secure_password@postgres:5432/kmrl_db
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_URL=http://qdrant:6333
      - MINIO_ENDPOINT=minio:9000
    depends_on:
      - postgres
      - redis
      - qdrant
      - minio

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
  minio_data:
```

### Environment Variables
```bash
# Production settings
ENVIRONMENT=production
LOG_LEVEL=INFO

# Security
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://user:pass@prod-db:5432/kmrl_db
REDIS_URL=redis://prod-redis:6379/0

# Performance
CHUNK_SIZE_TOKENS=1000
CHUNK_OVERLAP_TOKENS=100
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is part of the KMRL Document Intelligence system.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Create an issue with detailed information
4. Contact the development team

---

**Happy Document Processing! 📄✨**



