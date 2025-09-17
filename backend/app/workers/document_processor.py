import logging
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from typing import List, Dict, Any
from io import BytesIO

from ..database import SessionLocal, minio_client, MINIO_BUCKET, qdrant_client
from ..models import Document, Chunk, Task, Summary, SummaryLevel, TaskPriority, TaskStatus
from ..services import document_service
from ..nlp import generate_embeddings, extract_entities, generate_summary, extract_tasks

logger = logging.getLogger(__name__)

def process_document(doc_id: int):
    """Main document processing function"""
    logger.info(f"🚀 Starting document processing for document {doc_id}")
    
    db = SessionLocal()
    
    try:
        # Get document
        document = db.query(Document).filter(Document.id == doc_id).first()
        if not document:
            logger.error(f"Document {doc_id} not found")
            return
        
        # Update status to processing
        document.status = 'processing'
        db.commit()
        
        # Get document text
        text_content = ""
        if document.content:
            text_content = document.content
        elif document.file_path:
            # Download file from MinIO and extract text
            try:
                file_obj = minio_client.get_object(MINIO_BUCKET, document.file_path)
                file_content = file_obj.read()
                file_obj.close()
                
                # Try multiple extractors for PDF
                if document.file_type == 'application/pdf' or (document.file_name and document.file_name.lower().endswith('.pdf')):
                    try:
                        from PyPDF2 import PdfReader
                        reader = PdfReader(BytesIO(file_content))
                        extracted = []
                        for page in reader.pages:
                            try:
                                extracted.append(page.extract_text() or "")
                            except Exception:
                                extracted.append("")
                        text_content = "\n".join([t for t in extracted if t])
                    except Exception as e_pdf:
                        logger.warning(f"PyPDF2 failed to read PDF: {e_pdf}")
                        text_content = ""
                    
                    if not text_content.strip():
                        try:
                            import pdfplumber
                            with pdfplumber.open(BytesIO(file_content)) as pdf:
                                pages_text = []
                                for page in pdf.pages:
                                    try:
                                        pages_text.append(page.extract_text() or "")
                                    except Exception:
                                        pages_text.append("")
                                text_content = "\n".join([t for t in pages_text if t])
                        except Exception as e_pl:
                            logger.warning(f"pdfplumber failed to extract text: {e_pl}")
                            text_content = ""
                else:
                    # Treat as text-like content
                    try:
                        text_content = file_content.decode('utf-8', errors='ignore')
                    except Exception:
                        text_content = ""
                
            except Exception as e:
                logger.error(f"Failed to extract text from file: {e}")
                text_content = document.content or ""
        
        if not text_content.strip():
            logger.warning(f"No text content found for document {doc_id}")
            document.status = 'failed'
            db.commit()
            return
        
        # Process document
        logger.info(f"📄 Processing document {doc_id} with {len(text_content)} characters")
        
        # 1. Generate document summary
        summary_text = generate_document_summary(text_content)
        if summary_text:
            summary = Summary(
                doc_id=doc_id,
                level=SummaryLevel.DOCUMENT,
                text=summary_text,
                method="extractive"
            )
            db.add(summary)
            document.summary = summary_text
        
        # 2. Chunk the document
        chunks = chunk_document(text_content, doc_id)
        
        # 3. Process chunks (embeddings, entities, tasks)
        tasks = []
        for chunk in chunks:
            # Store chunk
            db.add(chunk)
            db.flush()  # Get chunk ID
            
            # Generate embeddings
            try:
                embeddings = generate_embeddings(chunk.text)
                vector_id = document_service._generate_vector_id(chunk.id)
                
                # Store in Qdrant
                point = {
                    "id": vector_id,
                    "vector": embeddings,
                    "payload": {
                        "document_id": doc_id,
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
                logger.info(f"✅ Stored chunk {chunk.id} in Qdrant with vector ID {vector_id}")
                
            except Exception as e:
                logger.error(f"Failed to generate embeddings for chunk {chunk.id}: {e}")
            
            # Extract entities
            try:
                entities = extract_entities(chunk.text)
                chunk.nlp_metadata = {"entities": entities}
                logger.info(f"🏷️ Extracted {len(entities)} entities from chunk {chunk.id}")
            except Exception as e:
                logger.error(f"Failed to extract entities from chunk {chunk.id}: {e}")
            
            # Generate chunk summary
            try:
                chunk_summary = generate_chunk_summary(chunk.text)
                chunk.summary = chunk_summary
            except Exception as e:
                logger.error(f"Failed to generate chunk summary for chunk {chunk.id}: {e}")
            
            # Extract tasks from chunk
            try:
                chunk_tasks = extract_tasks_from_chunk(chunk.text, doc_id, chunk.id)
                tasks.extend(chunk_tasks)
                logger.info(f"📋 Extracted {len(chunk_tasks)} tasks from chunk {chunk.id}")
            except Exception as e:
                logger.error(f"Failed to extract tasks from chunk {chunk.id}: {e}")
        
        # 4. Store tasks
        for task in tasks:
            db.add(task)
        
        # 5. Update document status
        document.is_processed = True
        document.status = 'processed'
        document.processed_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"✅ Successfully processed document {doc_id}: {len(chunks)} chunks, {len(tasks)} tasks")
        
        # Cache results in Redis
        try:
            document_service.cache_document_results(doc_id, {
                "summary": summary_text,
                "chunks_count": len(chunks),
                "tasks_count": len(tasks),
                "processed_at": document.processed_at.isoformat()
            })
        except Exception as e:
            logger.warning(f"Failed to cache results: {e}")
        
        return {
            "document_id": doc_id,
            "status": "processed",
            "chunks": len(chunks),
            "tasks": len(tasks),
            "summary_generated": bool(summary_text)
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to process document {doc_id}: {e}")
        
        # Update document status to failed
        document.status = 'failed'
        db.commit()
        
        raise
    finally:
        db.close()

def chunk_document(text: str, document_id: int) -> List[Chunk]:
    """Split document text into chunks"""
    chunks = []
    
    # Simple chunking by sentences and paragraphs
    paragraphs = text.split('\n\n')
    chunk_no = 1
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # If paragraph is too long, split by sentences
        if len(paragraph) > 1000:
            sentences = paragraph.split('. ')
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) > 1000 and current_chunk:
                    # Create chunk
                    chunk = Chunk(
                        doc_id=document_id,
                        chunk_no=chunk_no,
                        text=current_chunk.strip(),
                        text_excerpt=current_chunk.strip()[:200],
                        page_no=1  # Default page number
                    )
                    chunks.append(chunk)
                    chunk_no += 1
                    current_chunk = sentence
                else:
                    current_chunk += ". " + sentence if current_chunk else sentence
                    
            # Add remaining text as chunk
            if current_chunk.strip():
                chunk = Chunk(
                    doc_id=document_id,
                    chunk_no=chunk_no,
                    text=current_chunk.strip(),
                    text_excerpt=current_chunk.strip()[:200],
                    page_no=1
                )
                chunks.append(chunk)
                chunk_no += 1
        else:
            # Paragraph is small enough, use as single chunk
            chunk = Chunk(
                doc_id=document_id,
                chunk_no=chunk_no,
                text=paragraph,
                text_excerpt=paragraph[:200],
                page_no=1
            )
            chunks.append(chunk)
            chunk_no += 1
    
    return chunks

def generate_document_summary(text: str) -> str:
    """Generate summary for entire document"""
    try:
        # Extract key sections and create a structured summary
        sections = []
        
        # Look for section headers
        import re
        section_pattern = r'SECTION \d+: ([^\\n]+)'
        section_matches = re.findall(section_pattern, text)
        
        if section_matches:
            sections.append("This document covers the following key areas:")
            for i, section in enumerate(section_matches, 1):
                sections.append(f"{i}. {section}")
        
        # Extract key sentences with important keywords
        sentences = re.split(r'[.!?]+', text)
        key_sentences = []
        
        important_keywords = ['safety', 'procedures', 'emergency', 'maintenance', 'training', 'staff', 'metro', 'rail']
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and any(keyword in sentence.lower() for keyword in important_keywords):
                key_sentences.append(sentence)
                if len(key_sentences) >= 3:
                    break
        
        if key_sentences:
            if sections:
                sections.append("\\nKey points:")
                sections.extend(key_sentences[:3])
            else:
                sections = key_sentences[:3]
        
        if sections:
            return '. '.join(sections) + '.'
        else:
            # Fallback to first few sentences
            sentences = text.split('. ')
            if len(sentences) <= 3:
                return text
            summary_sentences = sentences[:3]
            return '. '.join(summary_sentences) + '.'
            
    except Exception as e:
        logger.error(f"Failed to generate document summary: {e}")
        return ""

def generate_chunk_summary(text: str) -> str:
    """Generate summary for a chunk"""
    try:
        # Simple extractive summary - take first sentence
        sentences = text.split('. ')
        if sentences:
            return sentences[0] + '.' if not sentences[0].endswith('.') else sentences[0]
        return ""
    except Exception as e:
        logger.error(f"Failed to generate chunk summary: {e}")
        return ""

def extract_tasks_from_chunk(text: str, document_id: int, chunk_id: str) -> List[Task]:
    """Extract actionable tasks from chunk text"""
    tasks = []
    
    try:
        # More comprehensive task extraction patterns
        task_patterns = [
            # Action verbs + objects
            r'(?:must|should|need to|required to|have to)\s+([^.]*?)(?:\.|$)',
            r'(?:implement|create|build|develop|install|configure|setup|update|fix|resolve|check|verify|test|review|approve|submit|send|complete|follow|inspect|contact|evacuate)\s+([^.]*?)(?:\.|$)',
            r'(?:please|kindly)\s+([^.]*?)(?:\.|$)',
            r'(?:all|staff|team|maintenance team|new staff)\s+([^.]*?)(?:\.|$)',
        ]
        
        import re
        
        # Extract sentences that contain actionable content
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 10:
                continue
                
            # Check if sentence contains actionable patterns
            is_actionable = False
            priority_value = TaskPriority.MEDIUM
            
            # Check for high priority keywords
            if any(word in sentence.lower() for word in ['urgent', 'critical', 'immediate', 'asap', 'emergency', 'must', 'required']):
                is_actionable = True
                priority_value = TaskPriority.HIGH
            # Check for medium priority keywords
            elif any(word in sentence.lower() for word in ['should', 'need to', 'implement', 'create', 'check', 'review', 'contact', 'evacuate', 'inspect']):
                is_actionable = True
                priority_value = TaskPriority.MEDIUM
            # Check for low priority keywords
            elif any(word in sentence.lower() for word in ['optional', 'nice to have', 'later', 'when possible']):
                is_actionable = True
                priority_value = TaskPriority.LOW
            
            if is_actionable:
                # Clean up the sentence
                cleaned_sentence = sentence.strip()
                if cleaned_sentence.endswith(','):
                    cleaned_sentence = cleaned_sentence[:-1]
                
                # Skip if too short or too long
                if 15 <= len(cleaned_sentence) <= 200:
                    task = Task(
                        doc_id=document_id,
                        source_chunk_id=chunk_id,
                        task_text=cleaned_sentence,
                        priority=priority_value,
                        status=TaskStatus.OPEN,
                        extracted_by='rule-based'
                    )
                    tasks.append(task)
    
    except Exception as e:
        logger.error(f"Failed to extract tasks from chunk: {e}")
    
    return tasks