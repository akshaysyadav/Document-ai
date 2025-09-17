import json
import uuid
import hashlib
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, UploadFile
import redis
from minio import Minio
from qdrant_client import QdrantClient
import logging
from io import BytesIO
import os

from .models import Document, DocumentCreate, DocumentUpdate, DocumentResponse, DocumentPage, TextChunk
from .database import redis_client, minio_client, qdrant_client, MINIO_BUCKET

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        self.redis_prefix = "doc:"
        self.collection_name = "documents"
        
    def _generate_cache_key(self, doc_id: int) -> str:
        """Generate Redis cache key"""
        return f"{self.redis_prefix}{doc_id}"
    
    def _generate_vector_id(self, doc_id: int) -> str:
        """Generate Qdrant vector ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _generate_file_path(self, filename: str, doc_uuid: str) -> str:
        """Generate MinIO file path"""
        extension = os.path.splitext(filename)[1]
        return f"documents/{doc_uuid}/{filename}"
    
    def _cache_document(self, document: Document):
        """Cache document in Redis"""
        try:
            doc_data = {
                "id": document.id,
                "uuid": document.uuid,
                "title": document.title,
                "description": document.description,
                "content": document.content,
                "file_path": document.file_path,
                "file_name": document.file_name,
                "file_size": document.file_size,
                "file_type": document.file_type,
                "tags": document.tags,
                "metadata": document.doc_metadata,
                "vector_id": document.vector_id,
                "is_processed": document.is_processed,
                "status": document.status,
                "processed_at": document.processed_at.isoformat() if document.processed_at else None,
                "created_at": document.created_at.isoformat(),
                "updated_at": document.updated_at.isoformat()
            }
            
            cache_key = self._generate_cache_key(document.id)
            redis_client.setex(cache_key, 3600, json.dumps(doc_data, default=str))  # 1 hour TTL
            logger.info(f"Cached document {document.id} in Redis")
        except Exception as e:
            logger.error(f"Failed to cache document {document.id}: {e}")
    
    def _invalidate_cache(self, doc_id: int):
        """Remove document from cache"""
        try:
            cache_key = self._generate_cache_key(doc_id)
            redis_client.delete(cache_key)
            logger.info(f"Invalidated cache for document {doc_id}")
        except Exception as e:
            logger.error(f"Failed to invalidate cache for document {doc_id}: {e}")
    
    def _get_from_cache(self, doc_id: int) -> Optional[Dict]:
        """Get document from cache"""
        try:
            cache_key = self._generate_cache_key(doc_id)
            cached_data = redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Failed to get document {doc_id} from cache: {e}")
        return None
    
    def _store_vector(self, doc_id: int, content: str):
        """Store document vector in Qdrant"""
        try:
            if not content:
                return
                
            # Simple text embedding (in production, use proper embedding model)
            vector = self._simple_text_embedding(content)
            vector_id = self._generate_vector_id(doc_id)
            
            qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[{
                    "id": vector_id,
                    "vector": vector,
                    "payload": {
                        "doc_id": doc_id,
                        "content": content[:500]  # Store first 500 chars
                    }
                }]
            )
            logger.info(f"Stored vector for document {doc_id} in Qdrant")
        except Exception as e:
            logger.error(f"Failed to store vector for document {doc_id}: {e}")
    
    def _delete_vector(self, doc_id: int):
        """Delete document vector from Qdrant"""
        try:
            vector_id = self._generate_vector_id(doc_id)
            qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=[vector_id]
            )
            logger.info(f"Deleted vector for document {doc_id} from Qdrant")
        except Exception as e:
            logger.error(f"Failed to delete vector for document {doc_id}: {e}")
    
    def _simple_text_embedding(self, text: str) -> List[float]:
        """Simple text embedding (replace with proper embedding model)"""
        # This is a placeholder - use proper embedding models like sentence-transformers
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        # Convert to 384-dimensional vector
        vector = []
        for i in range(384):
            byte_index = i % len(hash_bytes)
            vector.append((hash_bytes[byte_index] - 128) / 128.0)
        return vector
    
    def _upload_file(self, file: UploadFile, doc_uuid: str) -> Dict[str, Any]:
        """Upload file to MinIO"""
        try:
            file_path = self._generate_file_path(file.filename, doc_uuid)
            
            # Reset file pointer
            file.file.seek(0)
            file_data = file.file.read()
            file_size = len(file_data)
            
            # Upload to MinIO
            minio_client.put_object(
                MINIO_BUCKET,
                file_path,
                BytesIO(file_data),
                file_size,
                content_type=file.content_type
            )
            
            logger.info(f"Uploaded file {file.filename} to MinIO at {file_path}")
            
            return {
                "file_path": file_path,
                "file_name": file.filename,
                "file_size": file_size,
                "file_type": file.content_type
            }
        except Exception as e:
            logger.error(f"Failed to upload file {file.filename}: {e}")
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    
    def _delete_file(self, file_path: str):
        """Delete file from MinIO"""
        try:
            if file_path:
                minio_client.remove_object(MINIO_BUCKET, file_path)
                logger.info(f"Deleted file {file_path} from MinIO")
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
    
    def create_document(self, db: Session, document: DocumentCreate, file: Optional[UploadFile] = None) -> Document:
        """Create a new document with full sync"""
        try:
            # Create document in database
            doc_uuid = str(uuid.uuid4())
            db_document = Document(
                uuid=doc_uuid,
                title=document.title,
                description=document.description,
                content=document.content,
                tags=document.tags,
                doc_metadata=document.doc_metadata,
                is_processed=False
            )
            
            # Handle file upload if provided
            if file:
                file_info = self._upload_file(file, doc_uuid)
                db_document.file_path = file_info["file_path"]
                db_document.file_name = file_info["file_name"]
                db_document.file_size = file_info["file_size"]
                db_document.file_type = file_info["file_type"]
            
            # Save to database
            db.add(db_document)
            db.commit()
            db.refresh(db_document)
            
            # Store vector ID
            vector_id = self._generate_vector_id(db_document.id)
            db_document.vector_id = vector_id
            db.commit()
            
            # Sync to other systems
            self._cache_document(db_document)
            if db_document.content:
                self._store_vector(db_document.id, db_document.content)
            
            logger.info(f"Created document {db_document.id} with full sync")
            return db_document
            
        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Document creation failed: {str(e)}")
    
    def get_document(self, db: Session, doc_id: int) -> Optional[Document]:
        """Get document from database (cache disabled for consistency)"""
        try:
            # Get from database directly for consistency
            document = db.query(Document).filter(Document.id == doc_id).first()
            if document:
                logger.info(f"Retrieved document {doc_id} from database")
            
            return document
            
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Document retrieval failed: {str(e)}")
    
    def get_documents(self, db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Document]:
        """Get list of documents with optional search"""
        try:
            query = db.query(Document)
            
            if search:
                search_filter = or_(
                    Document.title.ilike(f"%{search}%"),
                    Document.description.ilike(f"%{search}%"),
                    Document.content.ilike(f"%{search}%")
                )
                query = query.filter(search_filter)
            
            documents = query.offset(skip).limit(limit).all()
            logger.info(f"Retrieved {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to get documents: {e}")
            raise HTTPException(status_code=500, detail=f"Documents retrieval failed: {str(e)}")
    
    def update_document(self, db: Session, doc_id: int, document: DocumentUpdate, file: Optional[UploadFile] = None) -> Optional[Document]:
        """Update document with full sync"""
        try:
            # Get existing document
            db_document = db.query(Document).filter(Document.id == doc_id).first()
            if not db_document:
                return None
            
            # Update fields
            update_data = document.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_document, field, value)
            
            # Handle file upload if provided
            if file:
                # Delete old file
                if db_document.file_path:
                    self._delete_file(db_document.file_path)
                
                # Upload new file
                file_info = self._upload_file(file, db_document.uuid)
                db_document.file_path = file_info["file_path"]
                db_document.file_name = file_info["file_name"]
                db_document.file_size = file_info["file_size"]
                db_document.file_type = file_info["file_type"]
            
            # Save to database
            db.commit()
            db.refresh(db_document)
            
            # Sync to other systems
            self._invalidate_cache(doc_id)
            self._cache_document(db_document)
            
            if db_document.content:
                self._store_vector(db_document.id, db_document.content)
            
            logger.info(f"Updated document {doc_id} with full sync")
            return db_document
            
        except Exception as e:
            logger.error(f"Failed to update document {doc_id}: {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Document update failed: {str(e)}")
    
    def delete_document(self, db: Session, doc_id: int) -> bool:
        """Delete document with full cleanup"""
        try:
            # Get document
            document = db.query(Document).filter(Document.id == doc_id).first()
            if not document:
                return False
            
            # Delete from all systems
            self._invalidate_cache(doc_id)
            self._delete_vector(doc_id)
            
            if document.file_path:
                self._delete_file(document.file_path)
            
            # Delete from database
            db.delete(document)
            db.commit()
            
            logger.info(f"Deleted document {doc_id} with full cleanup")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Document deletion failed: {str(e)}")
    
    def search_documents(self, db: Session, query_text: str, limit: int = 10) -> List[Document]:
        """Search documents using vector similarity"""
        try:
            # Generate query vector
            query_vector = self._simple_text_embedding(query_text)
            
            # Search in Qdrant
            search_results = qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            
            # Get document IDs from results
            doc_ids = [int(result.payload["doc_id"]) for result in search_results]
            
            # Get documents from database
            documents = db.query(Document).filter(Document.id.in_(doc_ids)).all()
            
            logger.info(f"Found {len(documents)} documents for search query")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            raise HTTPException(status_code=500, detail=f"Document search failed: {str(e)}")

# Create service instance
document_service = DocumentService()