from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import enum

Base = declarative_base()


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in-progress"
    DONE = "done"


class SummaryLevel(str, enum.Enum):
    DOCUMENT = "document"
    CHAPTER = "chapter"
    CHUNK = "chunk"

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
    status = Column(String, default="uploaded", index=True)  # uploaded, processing, processed, failed
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    chunks = relationship("Chunk", back_populates="document")
    summaries = relationship("Summary", back_populates="document")
    tasks = relationship("Task", back_populates="document")

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


class Chunk(Base):
    __tablename__ = "chunks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    doc_id = Column(Integer, ForeignKey("documents.id"), index=True)
    page_no = Column(Integer, nullable=True, index=True)
    chunk_no = Column(Integer, index=True)
    text = Column(Text, nullable=False)
    text_excerpt = Column(Text, nullable=False)  # First 200 chars
    embedding_id = Column(String, nullable=True, index=True)  # Qdrant point ID
    embedding_dim = Column(Integer, nullable=True)
    summary = Column(Text, nullable=True)
    nlp_metadata = Column(JSON, nullable=True)  # Entities, etc.
    status = Column(String, default="pending", index=True)  # pending, processing, processed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="chunks")


class Summary(Base):
    __tablename__ = "summaries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    doc_id = Column(Integer, ForeignKey("documents.id"), index=True)
    level = Column(Enum(SummaryLevel), nullable=False, index=True)
    text = Column(Text, nullable=False)
    method = Column(String, nullable=False)  # e.g., "hf-bart", "llm-prompt"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="summaries")


class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    doc_id = Column(Integer, ForeignKey("documents.id"), index=True)
    source_chunk_id = Column(String, ForeignKey("chunks.id"), nullable=True, index=True)
    task_text = Column(Text, nullable=False)
    assignee = Column(String, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, index=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.OPEN, index=True)
    extracted_by = Column(String, nullable=False)  # e.g., "rule-based", "llm"
    task_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="tasks")
    chunk = relationship("Chunk")

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
    status: Optional[str] = None
    processed_at: Optional[datetime] = None
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


# New Pydantic Models for Enhanced Pipeline
class ChunkResponse(BaseModel):
    id: str
    doc_id: int
    page_no: Optional[int]
    chunk_no: int
    text_excerpt: str
    summary: Optional[str]
    entities: Optional[List[Dict[str, Any]]]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class SummaryResponse(BaseModel):
    id: str
    doc_id: int
    level: SummaryLevel
    text: str
    method: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    id: str
    doc_id: int
    source_chunk_id: Optional[str]
    task_text: str
    assignee: Optional[str]
    due_date: Optional[datetime]
    priority: TaskPriority
    status: TaskStatus
    extracted_by: str
    task_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskUpdate(BaseModel):
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None


class DocumentResults(BaseModel):
    doc_id: int
    title: str
    summary: Optional[str]
    chunks: List[ChunkResponse]
    tasks: List[TaskResponse]
    status: str
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True