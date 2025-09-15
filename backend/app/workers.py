import redis
from rq import Worker, Queue, Connection
import os
import logging
from .ocr import extract_text_from_image
import tempfile
import uuid as uuidlib
from minio import Minio
from io import BytesIO
from PyPDF2 import PdfReader
from sqlalchemy.orm import Session
from .database import minio_client, MINIO_BUCKET, SessionLocal
from .models import DocumentPage, TextChunk
from .services import document_service
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
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

def process_document_ocr(document_id: int, file_path: str):
    """Process PDF: split pages, OCR per page, chunk, embed, upsert to Qdrant"""
    try:
        logger.info(f"Starting PDF processing for document: {document_id}")

        # Fetch the original PDF from MinIO into memory
        obj = minio_client.get_object(MINIO_BUCKET, file_path)
        pdf_bytes = obj.read()
        obj.close()
        obj.release_conn()

        # Read PDF pages
        reader = PdfReader(BytesIO(pdf_bytes))
        num_pages = len(reader.pages)

        db: Session = SessionLocal()
        total_chunks = 0
        try:
            for page_index in range(num_pages):
                page_no = page_index + 1

                # Extract text using PyPDF2 (basic); if empty, fallback to OCR image path later
                try:
                    page = reader.pages[page_index]
                    text = page.extract_text() or ""
                except Exception:
                    text = ""

                # If no text from PDF layer, skip OCR in this MVP (image OCR would need rasterization)
                ocr_conf = None

                # Store per-page text
                db_page = DocumentPage(
                    uuid=str(uuidlib.uuid4()),
                    doc_id=document_id,
                    page_no=page_no,
                    ocr_confidence=ocr_conf,
                    text=text or ""
                )
                db.add(db_page)
                db.commit()
                db.refresh(db_page)

                # Chunk page text
                chunks = _chunk_text_simple(text or "")
                if not chunks:
                    continue

                # Persist chunks
                for chunk_text in chunks:
                    db_chunk = TextChunk(
                        uuid=str(uuidlib.uuid4()),
                        doc_id=document_id,
                        page_no=page_no,
                        text=chunk_text
                    )
                    db.add(db_chunk)
                db.commit()

                # Embed and upsert to Qdrant with metadata
                for chunk_text in chunks:
                    vector = document_service._simple_text_embedding(chunk_text)
                    point_id = str(uuidlib.uuid4())
                    payload = {
                        "doc_id": document_id,
                        "page_no": page_no,
                        "text": chunk_text,
                    }
                    try:
                        from .database import qdrant_client
                        qdrant_client.upsert(
                            collection_name=document_service.collection_name,
                            points=[{"id": point_id, "vector": vector, "payload": payload}],
                        )
                    except Exception as e:
                        logger.warning(f"Qdrant upsert failed for doc {document_id} page {page_no}: {e}")

                total_chunks += len(chunks)

            logger.info(f"Completed PDF processing for doc {document_id}: pages={num_pages}, chunks={total_chunks}")
            return {"document_id": document_id, "pages": num_pages, "chunks": total_chunks}
        
    except Exception as e:
        logger.error(f"PDF processing failed for document {document_id}: {e}")
        raise

def _chunk_text_simple(text: str, max_chars: int = 1200) -> list[str]:
    if not text:
        return []
    chunks = []
    current = []
    size = 0
    for paragraph in text.split("\n\n"):
        p = paragraph.strip()
        if not p:
            continue
        if size + len(p) + 1 > max_chars and current:
            chunks.append("\n\n".join(current))
            current = [p]
            size = len(p)
        else:
            current.append(p)
            size += len(p) + 2
    if current:
        chunks.append("\n\n".join(current))
    return chunks

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
