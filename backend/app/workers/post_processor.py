import logging
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import SessionLocal
from ..models import Document, Chunk, Task, Summary

logger = logging.getLogger(__name__)

def document_post_process(document_id: int):
    """Post-process document after all chunks and tasks are created"""
    logger.info(f"Post-processing document {document_id}")
    
    db = SessionLocal()
    
    try:
        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.error(f"Document {document_id} not found")
            return
        
        # Count chunks and tasks
        chunks_count = db.query(Chunk).filter(Chunk.document_id == document_id).count()
        tasks_count = db.query(Task).filter(Task.document_id == document_id).count()
        
        # Update document metadata
        document.chunks_count = chunks_count
        document.tasks_count = tasks_count
        document.processed_at = datetime.utcnow()
        
        # Generate final summary if not exists
        if not document.summary:
            summary = db.query(Summary).filter(Summary.document_id == document_id).first()
            if summary:
                document.summary = summary.summary_text
        
        db.commit()
        
        logger.info(f"Post-processed document {document_id}: {chunks_count} chunks, {tasks_count} tasks")
        
        return {
            "document_id": document_id,
            "chunks_count": chunks_count,
            "tasks_count": tasks_count,
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Failed to post-process document {document_id}: {e}")
        raise
    finally:
        db.close()