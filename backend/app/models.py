from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    content = Column(Text)
    file_path = Column(String(500))  # MinIO file path
    file_name = Column(String(255))
    file_size = Column(Integer)
    file_type = Column(String(100))
    tags = Column(JSON)  # Store as JSON array
    doc_metadata = Column(JSON)  # Additional metadata
    vector_id = Column(String(100))  # Qdrant vector ID
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class DocumentPage(Base):
    __tablename__ = "document_pages"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    doc_id = Column(Integer, index=True)
    page_no = Column(Integer, index=True)
    ocr_confidence = Column(Float, nullable=True)
    text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class TextChunk(Base):
    __tablename__ = "text_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    doc_id = Column(Integer, index=True)
    page_no = Column(Integer, index=True)
    text = Column(Text)
    received_at = Column(DateTime(timezone=True), server_default=func.now())

# Pydantic Models for API
class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = []
    doc_metadata: Optional[Dict[str, Any]] = {}

class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    doc_metadata: Optional[Dict[str, Any]] = None

class DocumentResponse(BaseModel):
    id: int
    uuid: str
    title: str
    description: Optional[str]
    content: Optional[str]
    file_path: Optional[str]
    file_name: Optional[str]
    file_size: Optional[int]
    file_type: Optional[str]
    tags: Optional[List[str]]
    doc_metadata: Optional[Dict[str, Any]]
    vector_id: Optional[str]
    is_processed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DocumentList(BaseModel):
    documents: List[DocumentResponse]
    total: int
    page: int
    size: int
    pages: int

class FileUploadResponse(BaseModel):
    file_path: str
    file_name: str
    file_size: int
    file_type: str
    message: str