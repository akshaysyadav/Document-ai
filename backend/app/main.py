from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from datetime import datetime
import logging

# Import our modules
from .db import engine, Base
from .qdrant_client import qdrant_client
from .minio_client import minio_client
from .database import init_db, init_minio, init_qdrant, MINIO_BUCKET
from .routes import router as documents_router

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
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://frontend:5173",
        "http://localhost:3000",
        "http://frontend:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized successfully")
        
        # Initialize MinIO
        init_minio()
        logger.info("MinIO initialized successfully")
        
        # Initialize Qdrant
        init_qdrant()
        logger.info("Qdrant initialized successfully")
        
        # Test connections
        try:
            collections = qdrant_client.get_collections()
            logger.info(f"Qdrant connected successfully. Collections: {collections}")
        except Exception as e:
            logger.warning(f"Qdrant connection failed: {e}")
        
        # Test MinIO connection and ensure bucket exists
        try:
            if not minio_client.bucket_exists(MINIO_BUCKET):
                minio_client.make_bucket(MINIO_BUCKET)
                logger.info(f"Created MinIO bucket: {MINIO_BUCKET}")
            else:
                logger.info(f"MinIO bucket exists: {MINIO_BUCKET}")
        except Exception as e:
            logger.warning(f"MinIO connection failed: {e}")
            
    except Exception as e:
        logger.error(f"Startup failed: {e}")

# Include routers
app.include_router(documents_router)

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
        from .db import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        status["database"] = "healthy"
    except Exception as e:
        status["database"] = f"error: {str(e)}"
    
    # Check Qdrant
    try:
        qdrant_client.get_collections()
        status["qdrant"] = "healthy"
    except Exception as e:
        status["qdrant"] = f"error: {str(e)}"
    
    # Check MinIO
    try:
        minio_client.list_buckets()
        status["minio"] = "healthy"
    except Exception as e:
        status["minio"] = f"error: {str(e)}"
    
    # Check Redis
    try:
        import redis
        r = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))
        r.ping()
        status["redis"] = "healthy"
    except Exception as e:
        status["redis"] = f"error: {str(e)}"
    
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
