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
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import re

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
        """Get document with cache priority"""
        try:
            # Try cache first
            cached_doc = self._get_from_cache(doc_id)
            if cached_doc:
                logger.info(f"Retrieved document {doc_id} from cache")
                return cached_doc
            
            # Get from database
            document = db.query(Document).filter(Document.id == doc_id).first()
            if document:
                self._cache_document(document)
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

class DocumentAnalysisService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.summarizer = None
        self.task_extractor = None
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize HuggingFace models for summarization and task extraction"""
        try:
            # Use smaller models for CPU or larger models for GPU
            if self.device == "cuda":
                summarization_model = "facebook/bart-large-cnn"
                task_model = "google/flan-t5-base"
            else:
                summarization_model = "facebook/bart-base"
                task_model = "google/flan-t5-small"
            
            logger.info(f"Loading models on {self.device}...")
            
            # Initialize summarization pipeline
            self.summarizer = pipeline(
                "summarization",
                model=summarization_model,
                device=0 if self.device == "cuda" else -1,
                max_length=150,
                min_length=30,
                do_sample=False
            )
            
            # Initialize task extraction pipeline
            self.task_extractor = pipeline(
                "text2text-generation",
                model=task_model,
                device=0 if self.device == "cuda" else -1
            )
            
            logger.info(f"Models loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {e}")
            # Fallback to simple text processing if models fail
            self.summarizer = None
            self.task_extractor = None
    
    def generate_summary(self, text: str) -> str:
        """Generate a concise summary of the document text"""
        if not text or not text.strip():
            return "No content available for summary."
            
        try:
            # Limit text length for processing
            max_input_length = 1024 if self.device == "cuda" else 512
            truncated_text = text[:max_input_length] if len(text) > max_input_length else text
            
            if self.summarizer:
                # Use AI model for summarization
                result = self.summarizer(truncated_text)
                summary = result[0]['summary_text']
                logger.info(f"Generated AI summary of length {len(summary)}")
                return summary
            else:
                # Fallback to simple extraction
                return self._simple_summary(truncated_text)
                
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return self._simple_summary(text)
    
    def extract_tasks(self, text: str) -> List[str]:
        """Extract actionable tasks from the document text"""
        if not text or not text.strip():
            return []
            
        try:
            if self.task_extractor:
                # Use AI model for task extraction
                prompt = f"""Extract actionable tasks, todos, deadlines, and responsibilities from this text. 
                List only specific tasks that need to be done. Format as a simple list:
                
                {text[:800]}"""  # Limit input length
                
                result = self.task_extractor(prompt, max_length=200, num_return_sequences=1)
                generated_text = result[0]['generated_text']
                
                # Parse the generated text into individual tasks
                tasks = self._parse_generated_tasks(generated_text)
                logger.info(f"Extracted {len(tasks)} tasks using AI model")
                return tasks
            else:
                # Fallback to pattern-based extraction
                return self._pattern_based_task_extraction(text)
                
        except Exception as e:
            logger.error(f"Task extraction failed: {e}")
            return self._pattern_based_task_extraction(text)
    
    def _simple_summary(self, text: str) -> str:
        """Simple fallback summarization using first few sentences"""
        sentences = text.split('. ')
        if len(sentences) <= 2:
            return text[:200] + "..." if len(text) > 200 else text
        
        # Take first 2-3 sentences
        summary_sentences = sentences[:3]
        summary = '. '.join(summary_sentences)
        
        if len(summary) > 300:
            summary = summary[:300] + "..."
        
        return summary
    
    def _parse_generated_tasks(self, generated_text: str) -> List[str]:
        """Parse AI-generated text into individual tasks"""
        tasks = []
        
        # Split by common delimiters
        lines = generated_text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Remove common prefixes
            line = re.sub(r'^[-*•\d+\.\)\s]+', '', line).strip()
            
            # Filter out empty lines and non-task content
            if line and len(line) > 10 and any(keyword in line.lower() for keyword in 
                ['task', 'todo', 'complete', 'finish', 'review', 'submit', 'prepare', 'schedule', 'contact', 'send', 'create', 'update']):
                # Clean up the task
                if line.endswith('.'):
                    line = line[:-1]
                tasks.append(line)
        
        return tasks[:10]  # Limit to 10 tasks
    
    def _pattern_based_task_extraction(self, text: str) -> List[str]:
        """Fallback pattern-based task extraction"""
        tasks = []
        
        # Common task patterns
        task_patterns = [
            r'(?:need to|must|should|have to|required to)\s+([^.!?\n]+)',
            r'(?:todo|to-do|task)[:;\s]*([^.!?\n]+)',
            r'(?:deadline|due)[:;\s]*([^.!?\n]+)',
            r'(?:action item|action)[:;\s]*([^.!?\n]+)',
            r'(?:responsibility|responsible for)[:;\s]*([^.!?\n]+)',
            r'(?:complete|finish|submit|prepare|schedule|contact|send|create|update)\s+([^.!?\n]+)',
        ]
        
        for pattern in task_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                task = match.group(1).strip()
                if len(task) > 10 and len(task) < 200:  # Reasonable task length
                    tasks.append(task)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tasks = []
        for task in tasks:
            task_lower = task.lower()
            if task_lower not in seen:
                seen.add(task_lower)
                unique_tasks.append(task)
        
        return unique_tasks[:10]  # Limit to 10 tasks
    
    def analyze_document(self, text: str) -> Dict[str, Any]:
        """Perform complete document analysis: summary + task extraction"""
        logger.info(f"Starting document analysis for text of length {len(text)}")
        
        summary = self.generate_summary(text)
        tasks = self.extract_tasks(text)
        
        result = {
            "summary": summary,
            "tasks": tasks
        }
        
        logger.info(f"Document analysis completed: summary={len(summary)} chars, tasks={len(tasks)}")
        return result

# Create service instances
document_service = DocumentService()
document_analysis_service = DocumentAnalysisService()
