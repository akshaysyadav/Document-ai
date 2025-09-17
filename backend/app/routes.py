from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import io
import mimetypes
import logging
from minio.error import S3Error

logger = logging.getLogger(__name__)

from .database import get_db, minio_client, MINIO_BUCKET, health_check
<<<<<<< HEAD
from .models import DocumentCreate, DocumentUpdate, DocumentResponse, DocumentList, FileUploadResponse, DocumentAnalysisResponse
from .services_minimal import document_service, document_analysis_service
# from .workers import enqueue_ocr_job, enqueue_analysis_job  # Commented out for minimal version
=======
from .models import (
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentList, FileUploadResponse,
    ChunkResponse, SummaryResponse, TaskResponse, TaskUpdate, DocumentResults
)
from .services import document_service
from .workers import enqueue_document_processing
>>>>>>> 6cf60fbee093c047b118865411273cdd751d03a1

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("/", response_model=DocumentResponse)
async def create_document(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # JSON string of tags
    file: Optional[UploadFile] = File(None),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Create a new document with optional file upload"""
    try:
        # Parse tags if provided
        import json
        parsed_tags = []
        if tags:
            try:
                parsed_tags = json.loads(tags)
            except json.JSONDecodeError:
                parsed_tags = [tag.strip() for tag in tags.split(",")]
        
        # Create document data
        document_data = DocumentCreate(
            title=title,
            description=description,
            content=content,
            tags=parsed_tags
        )
        
        # Create document
        document = document_service.create_document(db, document_data, file)
<<<<<<< HEAD
        # Fire-and-forget background preprocessing if file present (disabled for minimal version)
        # if file and document.file_path:
        #     try:
        #         enqueue_ocr_job(document.id, document.file_path)
        #     except Exception:
        #         pass
=======
        # Trigger processing (queue or background task or inline)
        if document.file_path or document.content:
            try:
                from .settings import settings
                if settings.USE_QUEUE:
                    enqueue_document_processing(document.id)
                elif background_tasks is not None:
                    from .workers.document_processor import process_document
                    background_tasks.add_task(process_document, document.id)
                else:
                    from .workers.document_processor import process_document
                    process_document(document.id)
            except Exception as e:
                logger.warning(f"Processing dispatch failed: {e}. Attempting inline.")
                try:
                    from .workers.document_processor import process_document
                    process_document(document.id)
                except Exception as e2:
                    logger.warning(f"Inline processing failed: {e2}")
>>>>>>> 6cf60fbee093c047b118865411273cdd751d03a1
        return document
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=DocumentList)
async def get_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get list of documents with pagination and search"""
    try:
        documents = document_service.get_documents(db, skip, limit, search)
        
        # Get total count for pagination
        from .models import Document
        total_query = db.query(Document)
        if search:
            from sqlalchemy import or_
            search_filter = or_(
                Document.title.ilike(f"%{search}%"),
                Document.description.ilike(f"%{search}%"),
                Document.content.ilike(f"%{search}%")
            )
            total_query = total_query.filter(search_filter)
        
        total = total_query.count()
        pages = (total + limit - 1) // limit
        
        return DocumentList(
            documents=documents,
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            pages=pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific document by ID"""
    try:
        document = document_service.get_document(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # JSON string of tags
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Update a document with optional file upload"""
    try:
        # Parse tags if provided
        import json
        parsed_tags = None
        if tags:
            try:
                parsed_tags = json.loads(tags)
            except json.JSONDecodeError:
                parsed_tags = [tag.strip() for tag in tags.split(",")]
        
        # Create update data (only include provided fields)
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if content is not None:
            update_data["content"] = content
        if parsed_tags is not None:
            update_data["tags"] = parsed_tags
        
        document_update = DocumentUpdate(**update_data)
        
        # Update document
        document = document_service.update_document(db, document_id, document_update, file)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Delete a document"""
    try:
        success = document_service.delete_document(db, document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}/download")
async def download_file(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Download the file associated with a document"""
    try:
        # Get document
        document = document_service.get_document(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not document.file_path:
            raise HTTPException(status_code=404, detail="No file associated with this document")
        
        # Get file from MinIO
        try:
            file_object = minio_client.get_object(MINIO_BUCKET, document.file_path)
            file_data = file_object.read()
            
            # Determine content type
            content_type = document.file_type or mimetypes.guess_type(document.file_name)[0] or "application/octet-stream"
            
            # Create streaming response
            return StreamingResponse(
                io.BytesIO(file_data),
                media_type=content_type,
                headers={"Content-Disposition": f"attachment; filename={document.file_name}"}
            )
            
        except S3Error as e:
            raise HTTPException(status_code=404, detail="File not found in storage")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=List[DocumentResponse])
async def search_documents(
    query: str = Form(...),
    limit: int = Form(10),
    db: Session = Depends(get_db)
):
    """Search documents using vector similarity"""
    try:
        documents = document_service.search_documents(db, query, limit)
        return documents
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file_only(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a file without creating a document (for testing)"""
    try:
        import uuid
        doc_uuid = str(uuid.uuid4())
        
        # Upload file
        file_info = document_service._upload_file(file, doc_uuid)
        
        return FileUploadResponse(
            file_path=file_info["file_path"],
            file_name=file_info["file_name"],
            file_size=file_info["file_size"],
            file_type=file_info["file_type"],
            message="File uploaded successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{document_id}/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Analyze document for summary and tasks using AI models"""
    try:
        # Get document to verify it exists and user has access
        document = document_service.get_document(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Check if document already has analysis
        if hasattr(document, 'summary') and document.summary and hasattr(document, 'tasks') and document.tasks:
            # Return existing analysis
            return DocumentAnalysisResponse(
                summary=document.summary,
                tasks=document.tasks or []
            )
        
        # Enqueue background analysis job (disabled for minimal version - using sync analysis)
        # try:
        #     job = enqueue_analysis_job(document_id)
        #     logger.info(f"Enqueued analysis job {job.id} for document {document_id}")
        # except Exception as e:
        #     logger.error(f"Failed to enqueue analysis job for document {document_id}: {e}")
        
        # Perform synchronous analysis
        from .services_minimal import document_analysis_service
        from .models import Document, DocumentPage, TextChunk
        
        # Extract text content
        text_content = ""
        if hasattr(document, 'content') and document.content:
            text_content = document.content
        else:
            # Try to get text from pages or chunks
            pages = db.query(DocumentPage).filter(DocumentPage.doc_id == document_id).order_by(DocumentPage.page_no).all()
            if pages:
                text_content = "\n\n".join([page.text or "" for page in pages])
            
            if not text_content.strip():
                chunks = db.query(TextChunk).filter(TextChunk.doc_id == document_id).all()
                if chunks:
                    text_content = "\n".join([chunk.text or "" for chunk in chunks])
        
        if not text_content.strip():
            # If no content available, create a default analysis
            analysis_result = {
                "summary": f"Document '{document.title}' - No text content available for analysis.",
                "tasks": ["Review document content", "Add text content for better analysis"]
            }
        else:
            # Perform analysis
            analysis_result = document_analysis_service.analyze_document(text_content)
        
        # Update document
        db_document = db.query(Document).filter(Document.id == document_id).first()
        if db_document:
            db_document.summary = analysis_result["summary"]
            db_document.tasks = analysis_result["tasks"]
            db.commit()
        
        return DocumentAnalysisResponse(
            summary=analysis_result["summary"],
            tasks=analysis_result["tasks"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Health check endpoint
@router.get("/health")
async def documents_health():
    """Check health of all document-related services"""
    try:
        health = health_check()
        status_code = 200 if all(health.values()) else 503
        
        return {
            "status": "healthy" if all(health.values()) else "unhealthy",
            "services": health,
            "message": "All services operational" if all(health.values()) else "Some services are down"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "services": {},
            "message": f"Health check failed: {str(e)}"
        }


# Enhanced Pipeline Endpoints

@router.get("/{document_id}/results", response_model=DocumentResults)
async def get_document_results(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get comprehensive document processing results"""
    try:
        from .models import Document, Chunk, Summary, Task, SummaryLevel
        
        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get document summary
        document_summary = db.query(Summary).filter(
            Summary.doc_id == document_id,
            Summary.level == SummaryLevel.DOCUMENT
        ).first()
        
        # Get chunks
        chunks = db.query(Chunk).filter(Chunk.doc_id == document_id).all()
        chunk_responses = []
        for chunk in chunks:
            chunk_responses.append(ChunkResponse(
                id=chunk.id,
                doc_id=chunk.doc_id,
                page_no=chunk.page_no,
                chunk_no=chunk.chunk_no,
                text_excerpt=chunk.text_excerpt,
                text=chunk.text,
                summary=chunk.summary,
                entities=chunk.nlp_metadata.get("entities", []) if chunk.nlp_metadata else [],
                status=chunk.status,
                created_at=chunk.created_at
            ))
        
        # Get tasks
        tasks = db.query(Task).filter(Task.doc_id == document_id).all()
        task_responses = []
        for task in tasks:
            task_responses.append(TaskResponse(
                id=task.id,
                doc_id=task.doc_id,
                source_chunk_id=task.source_chunk_id,
                task_text=task.task_text,
                assignee=task.assignee,
                due_date=task.due_date,
                priority=task.priority,
                status=task.status,
                extracted_by=task.extracted_by,
                task_metadata=task.task_metadata,
                created_at=task.created_at,
                updated_at=task.updated_at
            ))
        
        return DocumentResults(
            doc_id=document.id,
            title=document.title,
            summary=document_summary.text if document_summary else None,
            chunks=chunk_responses,
            tasks=task_responses,
            status=document.status,
            processed_at=document.processed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/chunks", response_model=List[ChunkResponse])
async def get_document_chunks(
    document_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get chunks for a specific document"""
    try:
        from .models import Chunk
        
        # Verify document exists
        from .models import Document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get chunks
        chunks = db.query(Chunk).filter(
            Chunk.doc_id == document_id
        ).offset(skip).limit(limit).all()
        
        chunk_responses = []
        for chunk in chunks:
            chunk_responses.append(ChunkResponse(
                id=chunk.id,
                doc_id=chunk.doc_id,
                page_no=chunk.page_no,
                chunk_no=chunk.chunk_no,
                text_excerpt=chunk.text_excerpt,
                summary=chunk.summary,
                entities=chunk.nlp_metadata.get("entities", []) if chunk.nlp_metadata else [],
                status=chunk.status,
                created_at=chunk.created_at
            ))
        
        return chunk_responses
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/tasks", response_model=List[TaskResponse])
async def get_document_tasks(
    document_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get tasks for a specific document"""
    try:
        from .models import Task
        
        # Verify document exists
        from .models import Document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get tasks
        tasks = db.query(Task).filter(
            Task.doc_id == document_id
        ).offset(skip).limit(limit).all()
        
        task_responses = []
        for task in tasks:
            task_responses.append(TaskResponse(
                id=task.id,
                doc_id=task.doc_id,
                source_chunk_id=task.source_chunk_id,
                task_text=task.task_text,
                assignee=task.assignee,
                due_date=task.due_date,
                priority=task.priority,
                status=task.status,
                extracted_by=task.extracted_by,
                task_metadata=task.task_metadata,
                created_at=task.created_at,
                updated_at=task.updated_at
            ))
        
        return task_responses
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
):
    """Update a task"""
    try:
        from .models import Task
        
        # Get task
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update fields
        update_data = task_update.dict(exclude_unset=True)
        # Normalize due_date if provided as string (YYYY-MM-DD)
        if "due_date" in update_data and isinstance(update_data["due_date"], str) and update_data["due_date"]:
            try:
                from datetime import datetime
                update_data["due_date"] = datetime.fromisoformat(update_data["due_date"]) if "T" in update_data["due_date"] else datetime.strptime(update_data["due_date"], "%Y-%m-%d")
            except Exception:
                # Ignore parsing error and leave as-is; FastAPI/Pydantic may handle or field will be unchanged
                update_data.pop("due_date", None)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        db.commit()
        db.refresh(task)
        
        return TaskResponse(
            id=task.id,
            doc_id=task.doc_id,
            source_chunk_id=task.source_chunk_id,
            task_text=task.task_text,
            assignee=task.assignee,
            due_date=task.due_date,
            priority=task.priority,
            status=task.status,
            extracted_by=task.extracted_by,
            task_metadata=task.task_metadata,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: int,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Reprocess a document (useful for failed documents or after model updates)"""
    try:
        from .models import Document
        
        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Reset document status
        document.status = "uploaded"
        document.is_processed = False
        document.processed_at = None
        db.commit()
        
        # Dispatch processing based on settings
        try:
            from .settings import settings
            if settings.USE_QUEUE:
                enqueue_document_processing(document_id)
                return {"message": f"Document {document_id} queued for reprocessing"}
            elif background_tasks is not None:
                from .workers.document_processor import process_document
                background_tasks.add_task(process_document, document_id)
                return {"message": f"Document {document_id} reprocessing started in background"}
            else:
                from .workers.document_processor import process_document
                process_document(document_id)
                return {"message": f"Document {document_id} reprocessed directly"}
        except Exception as e2:
            raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e2)}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/report")
async def get_document_report(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed processing report for a document"""
    try:
        from .workers.post_processor import generate_document_report
        
        # Verify document exists
        from .models import Document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Generate report
        report = generate_document_report(document_id)
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}/results-legacy")
async def get_document_results_legacy(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Legacy results endpoint retained for backward compatibility."""
    try:
        # Get document
        from .models import Document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # This legacy implementation is intentionally minimal.
        return {"doc_id": document_id, "title": document.title}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{document_id}/reprocess-direct")
async def reprocess_document_direct(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Reprocess a document directly (bypasses queue)"""
    try:
        # Get document
        from .models import Document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Mark document for reprocessing
        document.is_processed = False
        document.status = 'uploaded'
        db.commit()
        
        # Process directly
        try:
            from .workers.document_processor import process_document
            result = process_document(document_id)
            return {"message": "Document reprocessed successfully", "document_id": document_id, "result": result}
        except Exception as e:
            logger.error(f"Failed to reprocess document: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to reprocess document: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{document_id}/process")
async def process_document_direct(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Process a document directly (bypasses Redis queue)"""
    try:
        # Get document
        from .models import Document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Process directly
        try:
            from .workers.document_processor import process_document
            result = process_document(document_id)
            return {"message": "Document processed successfully", "document_id": document_id, "result": result}
        except Exception as e:
            logger.error(f"Failed to process document: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))