import logging
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import SessionLocal, qdrant_client
from ..models import Chunk
from ..nlp import generate_embeddings, extract_entities
from ..services.document_services import DocumentService

logger = logging.getLogger(__name__)

def process_chunk(chunk_id: int):
    """Process individual chunk for embeddings and entities"""
    logger.info(f"Processing chunk {chunk_id}")
    
    db = SessionLocal()
    document_service = DocumentService()
    
    try:
        # Get chunk
        chunk = db.query(Chunk).filter(Chunk.id == chunk_id).first()
        if not chunk:
            logger.error(f"Chunk {chunk_id} not found")
            return
        
        # Generate embeddings
        try:
            embeddings = generate_embeddings(chunk.text)
            vector_id = document_service._generate_vector_id(chunk.id)
            
            # Store in Qdrant
            point = {
                "id": vector_id,
                "vector": embeddings,
                "payload": {
                    "document_id": chunk.doc_id,
                    "chunk_id": chunk.id,
                    "chunk_no": chunk.chunk_no,
                    "text": chunk.text,
                    "page_no": chunk.page_no
                }
            }
            
            qdrant_client.upsert(
                collection_name="documents",
                points=[point]
            )
            
            chunk.embedding_id = vector_id
            chunk.status = 'processed'
            logger.info(f"Stored chunk {chunk.id} in Qdrant with vector ID {vector_id}")
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings for chunk {chunk.id}: {e}")
        
        # Extract entities
        try:
            entities = extract_entities(chunk.text)
            chunk.nlp_metadata = {"entities": entities}
            logger.info(f"Extracted {len(entities)} entities from chunk {chunk.id}")
        except Exception as e:
            logger.error(f"Failed to extract entities from chunk {chunk.id}: {e}")
        
        db.commit()
        
        return {
            "chunk_id": chunk_id,
            "vector_id": chunk.embedding_id,
            "entities_count": len(chunk.nlp_metadata.get("entities", [])) if chunk.nlp_metadata else 0
        }
        
    except Exception as e:
        logger.error(f"Failed to process chunk {chunk_id}: {e}")
        raise
    finally:
        db.close()