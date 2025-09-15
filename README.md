# 🚀 KMRL Document Intelligence MVP

A comprehensive Document Intelligence System for KMRL built with modern technologies including FastAPI, React, and containerized services.

## 🏗️ Architecture

### Stack Overview

- **Frontend**: React + Vite + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI + Python
- **Database**: PostgreSQL (metadata)
- **Vector Database**: Qdrant (embeddings)
- **Object Storage**: MinIO (S3-compatible)
- **Queue System**: Redis + RQ
- **OCR**: Tesseract
- **NLP**: HuggingFace Transformers + spaCy
- **Deployment**: Docker + Docker Compose

### Services

- **Frontend** (Port 3000): React development server
- **Backend** (Port 8000): FastAPI application
- **PostgreSQL** (Port 5432): Metadata database
- **Redis** (Port 6379): Queue system
- **Qdrant** (Port 6333): Vector database + dashboard
- **MinIO** (Port 9000/9001): Object storage + console

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Setup Instructions

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd KMRL
   ```

2. **Copy environment file**

   ```bash
   cp .env.example .env
   ```

3. **Start all services**

   ```bash
   docker compose up --build
   ```

4. **Access the applications**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **MinIO Console**: http://localhost:9001
   - **Qdrant Dashboard**: http://localhost:6333/dashboard

### Service Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Check service status
curl http://localhost:8000/api/status
```

## 📁 Project Structure

```
KMRL/
├── docker-compose.yml          # Main orchestration file
├── .env                        # Environment variables
├── .env.example               # Environment template
├── README.md                  # This file
│
├── KMRL-Frontend/             # React frontend
│   ├── Dockerfile.frontend    # Frontend container
│   ├── src/                   # Source code
│   ├── package.json          # Dependencies
│   └── vite.config.ts        # Vite configuration
│
└── backend/                   # FastAPI backend
    ├── Dockerfile.backend     # Backend container
    ├── requirements.txt       # Python dependencies
    └── app/                   # Application code
        ├── main.py           # FastAPI entry point
        ├── db.py             # Database models
        ├── workers.py        # RQ workers
        ├── qdrant_client.py  # Vector DB client
        ├── minio_client.py   # Object storage client
        ├── ocr.py            # OCR processing
        └── nlp.py            # NLP processing
```

## 🛠️ Development

### Running Individual Services

**Frontend only:**

```bash
cd KMRL-Frontend
npm install
npm run dev
```

**Backend only:**

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

Key environment variables (see `.env.example` for full list):

- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `MINIO_ROOT_USER`: MinIO admin username
- `MINIO_ROOT_PASSWORD`: MinIO admin password
- `ENVIRONMENT`: Application environment (development/production)

### API Endpoints

#### Health & Status

- `GET /health` - Health check
- `GET /api/info` - API information
- `GET /api/status` - Service status

#### Future Endpoints (Coming Soon)

- `POST /api/documents/upload` - Upload documents
- `GET /api/documents` - List documents
- `GET /api/documents/{id}` - Get document details
- `POST /api/search` - Vector search

## 🔧 Services Configuration

### PostgreSQL

- **Host**: localhost:5432
- **Database**: kmrl_db
- **User**: kmrl_user
- **Password**: kmrl_password

### MinIO

- **API**: http://localhost:9000
- **Console**: http://localhost:9001
- **Access Key**: minioadmin
- **Secret Key**: minioadmin123

### Qdrant

- **API**: http://localhost:6333
- **Dashboard**: http://localhost:6333/dashboard

### Redis

- **Host**: localhost:6379
- **Database**: 0

## 📊 Monitoring & Debugging

### View Service Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
```

### Access Service Containers

```bash
# Backend container
docker compose exec backend bash

# Database container
docker compose exec postgres psql -U kmrl_user -d kmrl_db
```

### Check Service Health

```bash
# Backend health
curl http://localhost:8000/health

# Service status
curl http://localhost:8000/api/status
```

## 🧪 Testing

### API Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test API info
curl http://localhost:8000/api/info

# Test service status
curl http://localhost:8000/api/status
```

## 📦 Data Persistence

The following data is persisted using Docker volumes:

- **postgres_data**: PostgreSQL database files
- **redis_data**: Redis data files
- **qdrant_data**: Qdrant vector database files
- **minio_data**: MinIO object storage files

### Backup & Restore

```bash
# Backup
docker compose exec postgres pg_dump -U kmrl_user kmrl_db > backup.sql

# Restore
docker compose exec -T postgres psql -U kmrl_user -d kmrl_db < backup.sql
```

## 🚀 Deployment

### Production Setup

1. Update environment variables in `.env`
2. Set `ENVIRONMENT=production`
3. Configure proper passwords and secrets
4. Use production-ready Docker images
5. Set up reverse proxy (nginx)
6. Enable SSL/TLS

### Scaling

- Scale worker containers: `docker compose up --scale worker=3`
- Use external services in production (managed PostgreSQL, Redis, etc.)

## 🔍 Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in docker-compose.yml
2. **Memory issues**: Increase Docker memory limits
3. **Permission issues**: Check file permissions and user mappings

### Reset Everything

```bash
# Stop and remove all containers, networks, and volumes
docker compose down -v

# Remove images
docker compose down --rmi all

# Start fresh
docker compose up --build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

[Add your license information here]

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section
2. Review service logs
3. Create an issue in the repository

---

🚀 **Ready to process documents intelligently with KMRL!**
