#!/usr/bin/env python3
"""
Development setup script for KMRL Document AI Backend
"""
import os
import sys
import subprocess
import logging

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import init_db, init_minio, init_qdrant
from app.services.enhanced_qdrant import enhanced_qdrant_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_database():
    """Initialize database tables"""
    try:
        logger.info("Setting up database...")
        init_db()
        logger.info("✅ Database setup completed")
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        raise


def setup_minio():
    """Initialize MinIO buckets"""
    try:
        logger.info("Setting up MinIO...")
        init_minio()
        logger.info("✅ MinIO setup completed")
    except Exception as e:
        logger.error(f"❌ MinIO setup failed: {e}")
        raise


def setup_qdrant():
    """Initialize Qdrant collections"""
    try:
        logger.info("Setting up Qdrant...")
        init_qdrant()
        
        # Ensure enhanced collection exists
        enhanced_qdrant_service._ensure_collection_exists()
        logger.info("✅ Qdrant setup completed")
    except Exception as e:
        logger.error(f"❌ Qdrant setup failed: {e}")
        raise


def download_spacy_model():
    """Download spaCy English model"""
    try:
        logger.info("Downloading spaCy English model...")
        subprocess.run([
            sys.executable, "-m", "spacy", "download", "en_core_web_sm"
        ], check=True)
        logger.info("✅ spaCy model downloaded")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to download spaCy model: {e}")
        raise


def run_migrations():
    """Run Alembic migrations"""
    try:
        logger.info("Running database migrations...")
        subprocess.run([
            "alembic", "upgrade", "head"
        ], check=True)
        logger.info("✅ Migrations completed")
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️ Migrations failed (may not be needed): {e}")


def main():
    """Main setup function"""
    logger.info("🚀 Setting up KMRL Document AI Backend for development...")
    
    try:
        # Setup core services
        setup_database()
        setup_minio()
        setup_qdrant()
        
        # Download required models
        download_spacy_model()
        
        # Run migrations
        run_migrations()
        
        logger.info("🎉 Development setup completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Start Redis: docker run -d -p 6379:6379 redis:7-alpine")
        logger.info("2. Start Qdrant: docker run -d -p 6333:6333 qdrant/qdrant")
        logger.info("3. Start MinIO: docker run -d -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ':9001'")
        logger.info("4. Start backend: python -m app.main")
        logger.info("5. Start worker: python -m app.workers")
        
    except Exception as e:
        logger.error(f"💥 Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


