from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="KMRL Document Intelligence API",
    description="MVP Document Intelligence System for KMRL",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "KMRL Document Intelligence API",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🚀 KMRL Document Intelligence MVP API is running!",
        "docs": "/docs",
        "health": "/health",
        "timestamp": datetime.now().isoformat()
    }

# API info endpoint
@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "KMRL Document Intelligence API",
        "version": "1.0.0",
        "description": "MVP Document Intelligence System for KMRL",
        "features": {
            "document_upload": "Coming soon",
            "ocr_processing": "Coming soon", 
            "nlp_analysis": "Coming soon",
            "vector_search": "Coming soon",
            "metadata_storage": "Ready"
        },
        "services": {
            "database": "PostgreSQL",
            "vector_db": "Qdrant",
            "object_storage": "MinIO",
            "queue": "Redis + RQ",
            "ocr": "Tesseract",
            "nlp": "HuggingFace + spaCy"
        }
    }

# Service status endpoint
@app.get("/api/status")
async def service_status():
    """Check status of all services"""
    status = {
        "api": "healthy",
        "database": "unknown",
        "qdrant": "unknown", 
        "minio": "unknown",
        "redis": "unknown"
    }
    
    # Check database
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database=os.getenv("POSTGRES_DB", "kmrl_db"),
            user=os.getenv("POSTGRES_USER", "kmrl_user"),
            password=os.getenv("POSTGRES_PASSWORD", "kmrl_password")
        )
        conn.close()
        status["database"] = "healthy"
    except Exception as e:
        status["database"] = f"error: {str(e)}"
    
    # Check Qdrant
    try:
        import httpx
        response = httpx.get("http://localhost:6333/health", timeout=5)
        if response.status_code == 200:
            status["qdrant"] = "healthy"
        else:
            status["qdrant"] = f"error: status {response.status_code}"
    except Exception as e:
        status["qdrant"] = f"error: {str(e)}"
    
    # Check MinIO
    try:
        import httpx
        response = httpx.get("http://localhost:9000/minio/health/live", timeout=5)
        if response.status_code == 200:
            status["minio"] = "healthy"
        else:
            status["minio"] = f"error: status {response.status_code}"
    except Exception as e:
        status["minio"] = f"error: {str(e)}"
    
    # Check Redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        status["redis"] = "healthy"
    except Exception as e:
        status["redis"] = f"error: {str(e)}"
    
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
