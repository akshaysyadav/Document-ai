import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis
from qdrant_client import QdrantClient
from minio import Minio
import logging

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kmrl_user:kmrl_password@localhost:5432/kmrl_db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# RQ Queues
from rq import Queue
ocr_queue = Queue('ocr', connection=redis_client)
nlp_queue = Queue('nlp', connection=redis_client)
post_process_queue = Queue('post_process', connection=redis_client)

# Qdrant Configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# MinIO Configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin123")
MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

# MinIO bucket name
MINIO_BUCKET = "documents"

def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    from .models import Base
    Base.metadata.create_all(bind=engine)
    
def init_minio():
    """Initialize MinIO bucket"""
    try:
        if not minio_client.bucket_exists(MINIO_BUCKET):
            minio_client.make_bucket(MINIO_BUCKET)
            logging.info(f"Created MinIO bucket: {MINIO_BUCKET}")
        else:
            logging.info(f"MinIO bucket already exists: {MINIO_BUCKET}")
    except Exception as e:
        logging.error(f"Failed to initialize MinIO: {e}")

def init_qdrant():
    """Initialize Qdrant collection"""
    try:
        from qdrant_client.models import Distance, VectorParams
        
        collection_name = "documents"
        collections = qdrant_client.get_collections().collections
        
        if not any(c.name == collection_name for c in collections):
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            logging.info(f"Created Qdrant collection: {collection_name}")
        else:
            logging.info(f"Qdrant collection already exists: {collection_name}")
    except Exception as e:
        logging.error(f"Failed to initialize Qdrant: {e}")

def health_check():
    """Check health of all services"""
    health = {
        "database": False,
        "redis": False,
        "qdrant": False,
        "minio": False
    }
    
    # Check database
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health["database"] = True
    except Exception as e:
        logging.error(f"Database health check failed: {e}")
    
    # Check Redis
    try:
        redis_client.ping()
        health["redis"] = True
    except Exception as e:
        logging.error(f"Redis health check failed: {e}")
    
    # Check Qdrant
    try:
        qdrant_client.get_collections()
        health["qdrant"] = True
    except Exception as e:
        logging.error(f"Qdrant health check failed: {e}")
    
    # Check MinIO
    try:
        minio_client.list_buckets()
        health["minio"] = True
    except Exception as e:
        logging.error(f"MinIO health check failed: {e}")
    
    return health