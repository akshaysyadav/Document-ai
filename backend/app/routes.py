from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import io
import mimetypes
from minio.error import S3Error

from .database import get_db, minio_client, MINIO_BUCKET, health_check
from .models import DocumentCreate, DocumentUpdate, DocumentResponse, DocumentList, FileUploadResponse
from .services import document_service

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("/", response_model=DocumentResponse)
async def create_document(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # JSON string of tags
    file: Optional[UploadFile] = File(None),
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