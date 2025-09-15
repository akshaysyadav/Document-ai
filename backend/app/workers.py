import redis
from rq import Worker, Queue, Connection
import os
import logging
from .ocr import extract_text_from_image
from .nlp import generate_embeddings, extract_entities

logger = logging.getLogger(__name__)

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Initialize Redis connection
try:
    redis_conn = redis.from_url(REDIS_URL)
    redis_conn.ping()
    logger.info(f"Redis connected successfully: {REDIS_URL}")
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")
    redis_conn = None

# Queue definitions
ocr_queue = Queue('ocr', connection=redis_conn)
nlp_queue = Queue('nlp', connection=redis_conn)
default_queue = Queue(connection=redis_conn)

def process_document_ocr(document_id: str, file_path: str):
    """Process document OCR in background"""
    try:
        logger.info(f"Starting OCR processing for document: {document_id}")
        
        # Extract text using OCR
        extracted_text = extract_text_from_image(file_path)
        
        # Update document in database with OCR text
        from .db import SessionLocal, Document
        db = SessionLocal()
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.ocr_text = extracted_text
                document.status = "ocr_completed"
                db.commit()
                logger.info(f"OCR completed for document: {document_id}")
            else:
                logger.error(f"Document not found: {document_id}")
        finally:
            db.close()
            
        return {"document_id": document_id, "text_length": len(extracted_text)}
        
    except Exception as e:
        logger.error(f"OCR processing failed for document {document_id}: {e}")
        
        # Update document status to failed
        from .db import SessionLocal, Document
        db = SessionLocal()
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.status = "ocr_failed"
                db.commit()
        finally:
            db.close()
            
        raise

def process_document_nlp(document_id: str, text: str):
    """Process document NLP in background"""
    try:
        logger.info(f"Starting NLP processing for document: {document_id}")
        
        # Generate embeddings
        embeddings = generate_embeddings(text)
        
        # Extract entities
        entities = extract_entities(text)
        
        # Store embeddings in Qdrant
        from .qdrant_client import add_document_vector
        metadata = {
            "document_id": document_id,
            "entities": entities,
            "text_length": len(text)
        }
        add_document_vector(document_id, embeddings, metadata)
        
        # Update document status
        from .db import SessionLocal, Document
        db = SessionLocal()
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.status = "completed"
                db.commit()
                logger.info(f"NLP processing completed for document: {document_id}")
        finally:
            db.close()
            
        return {
            "document_id": document_id,
            "entities_count": len(entities),
            "embeddings_size": len(embeddings)
        }
        
    except Exception as e:
        logger.error(f"NLP processing failed for document {document_id}: {e}")
        
        # Update document status to failed
        from .db import SessionLocal, Document
        db = SessionLocal()
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.status = "nlp_failed"
                db.commit()
        finally:
            db.close()
            
        raise

def enqueue_ocr_job(document_id: str, file_path: str):
    """Enqueue OCR processing job"""
    if redis_conn is None:
        raise Exception("Redis connection not available")
        
    job = ocr_queue.enqueue(process_document_ocr, document_id, file_path)
    logger.info(f"Enqueued OCR job for document {document_id}: {job.id}")
    return job

def enqueue_nlp_job(document_id: str, text: str):
    """Enqueue NLP processing job"""
    if redis_conn is None:
        raise Exception("Redis connection not available")
        
    job = nlp_queue.enqueue(process_document_nlp, document_id, text)
    logger.info(f"Enqueued NLP job for document {document_id}: {job.id}")
    return job

def run_worker():
    """Run RQ worker"""
    if redis_conn is None:
        logger.error("Cannot start worker: Redis connection not available")
        return
        
    with Connection(redis_conn):
        worker = Worker(['ocr', 'nlp', 'default'])
        logger.info("Starting RQ worker...")
        worker.work()

if __name__ == '__main__':
    run_worker()
