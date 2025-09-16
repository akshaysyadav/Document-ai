"""
Tests for worker components
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import uuid

from app.workers.document_processor import process_document
from app.workers.chunk_processor import process_chunk
from app.workers.post_processor import document_post_process


class TestDocumentProcessor:
    """Test document processing worker functionality"""
    
    def test_process_document_success(self, db_session, sample_document, sample_pdf_bytes):
        """Test successful document processing"""
        
        # Mock MinIO operations
        with patch('app.database.minio_client') as mock_minio:
            mock_file_obj = Mock()
            mock_file_obj.read.return_value = sample_pdf_bytes
            mock_file_obj.close.return_value = None
            mock_file_obj.release_conn.return_value = None
            mock_minio.get_object.return_value = mock_file_obj
            
            # Mock PDF processing
            with patch('app.services.pdf_processor.pdf_processor_service') as mock_pdf_processor:
                mock_pdf_processor.extract_text_from_pdf.return_value = {
                    'pages': [
                        {
                            'page_number': 1,
                            'text': 'This is a test document with some content.',
                            'confidence': 0.95,
                            'extraction_method': 'test'
                        }
                    ],
                    'total_pages': 1,
                    'extraction_method': 'test',
                    'success': True,
                    'error': None
                }
                
                # Mock embedding service
                with patch('app.services.embedding.embedding_service') as mock_embedding:
                    mock_embedding.chunk_text_by_tokens.return_value = [
                        "This is a test chunk"
                    ]
                    
                    # Mock queue operations
                    with patch('app.database.ocr_queue') as mock_queue:
                        mock_job = Mock()
                        mock_job.id = "test-job-id"
                        mock_queue.enqueue.return_value = mock_job
                        
                        # Process document
                        result = process_document(sample_document.id)
                        
                        assert result['document_id'] == sample_document.id
                        assert result['pages_processed'] == 1
                        assert result['chunks_created'] == 1
                        assert result['status'] == "processing_enqueued"
    
    def test_process_document_not_found(self, db_session):
        """Test processing non-existent document"""
        
        with pytest.raises(ValueError, match="Document .* not found"):
            process_document(99999)
    
    def test_process_document_no_file_path(self, db_session, sample_document):
        """Test processing document without file path"""
        
        sample_document.file_path = None
        db_session.commit()
        
        with pytest.raises(ValueError, match="Document .* has no file path"):
            process_document(sample_document.id)
    
    def test_process_document_pdf_extraction_failure(self, db_session, sample_document, sample_pdf_bytes):
        """Test document processing with PDF extraction failure"""
        
        # Mock MinIO operations
        with patch('app.database.minio_client') as mock_minio:
            mock_file_obj = Mock()
            mock_file_obj.read.return_value = sample_pdf_bytes
            mock_file_obj.close.return_value = None
            mock_file_obj.release_conn.return_value = None
            mock_minio.get_object.return_value = mock_file_obj
            
            # Mock PDF processing failure
            with patch('app.services.pdf_processor.pdf_processor_service') as mock_pdf_processor:
                mock_pdf_processor.extract_text_from_pdf.return_value = {
                    'success': False,
                    'error': 'PDF extraction failed',
                    'pages': [],
                    'total_pages': 0
                }
                
                with pytest.raises(ValueError, match="PDF text extraction failed"):
                    process_document(sample_document.id)


class TestChunkProcessor:
    """Test chunk processing worker functionality"""
    
    def test_process_chunk_success(self, db_session, sample_document):
        """Test successful chunk processing"""
        
        from app.models import Chunk
        
        # Create test chunk
        chunk = Chunk(
            id=str(uuid.uuid4()),
            doc_id=sample_document.id,
            page_no=1,
            chunk_no=1,
            text="This is a test chunk for processing.",
            text_excerpt="This is a test chunk for processing.",
            status="pending"
        )
        db_session.add(chunk)
        db_session.commit()
        
        # Mock services
        with patch('app.services.embedding.embedding_service') as mock_embedding:
            mock_embedding.generate_embedding.return_value = [0.1] * 384
            
            with patch('app.services.enhanced_qdrant.enhanced_qdrant_service') as mock_qdrant:
                mock_qdrant.upsert_point.return_value = True
                
                with patch('app.nlp.extract_entities') as mock_entities:
                    mock_entities.return_value = [
                        {"text": "test", "label": "ORG", "start": 0, "end": 4}
                    ]
                    
                    with patch('app.services.task_extractor.task_extractor_service') as mock_task_extractor:
                        mock_task_extractor.extract_tasks.return_value = [
                            {
                                'task_text': 'Test task',
                                'doc_id': sample_document.id,
                                'source_chunk_id': chunk.id,
                                'assignee': None,
                                'due_date': None,
                                'priority': 'medium',
                                'status': 'open',
                                'extracted_by': 'rule-based',
                                'metadata': {}
                            }
                        ]
                        
                        # Process chunk
                        result = process_chunk(chunk.id)
                        
                        assert result['chunk_id'] == chunk.id
                        assert result['status'] == "processed"
                        assert result['embedding_dimension'] == 384
                        assert result['entities_count'] == 1
                        assert result['tasks_extracted'] == 1
                        
                        # Verify chunk was updated
                        db_session.refresh(chunk)
                        assert chunk.status == "processed"
                        assert chunk.embedding_dim == 384
                        assert chunk.embedding_id is not None
    
    def test_process_chunk_not_found(self, db_session):
        """Test processing non-existent chunk"""
        
        with pytest.raises(ValueError, match="Chunk .* not found"):
            process_chunk("non-existent-chunk-id")
    
    def test_process_chunk_embedding_failure(self, db_session, sample_document):
        """Test chunk processing with embedding generation failure"""
        
        from app.models import Chunk
        
        # Create test chunk
        chunk = Chunk(
            id=str(uuid.uuid4()),
            doc_id=sample_document.id,
            page_no=1,
            chunk_no=1,
            text="This is a test chunk for processing.",
            text_excerpt="This is a test chunk for processing.",
            status="pending"
        )
        db_session.add(chunk)
        db_session.commit()
        
        # Mock embedding failure
        with patch('app.services.embedding.embedding_service') as mock_embedding:
            mock_embedding.generate_embedding.side_effect = Exception("Embedding failed")
            
            with pytest.raises(Exception, match="Embedding failed"):
                process_chunk(chunk.id)
            
            # Verify chunk status was updated to failed
            db_session.refresh(chunk)
            assert chunk.status == "failed"
    
    def test_process_chunk_qdrant_failure(self, db_session, sample_document):
        """Test chunk processing with Qdrant storage failure"""
        
        from app.models import Chunk
        
        # Create test chunk
        chunk = Chunk(
            id=str(uuid.uuid4()),
            doc_id=sample_document.id,
            page_no=1,
            chunk_no=1,
            text="This is a test chunk for processing.",
            text_excerpt="This is a test chunk for processing.",
            status="pending"
        )
        db_session.add(chunk)
        db_session.commit()
        
        # Mock services
        with patch('app.services.embedding.embedding_service') as mock_embedding:
            mock_embedding.generate_embedding.return_value = [0.1] * 384
            
            with patch('app.services.enhanced_qdrant.enhanced_qdrant_service') as mock_qdrant:
                mock_qdrant.upsert_point.return_value = False  # Simulate failure
                
                with pytest.raises(Exception, match="Failed to store vector in Qdrant"):
                    process_chunk(chunk.id)


class TestPostProcessor:
    """Test post-processing worker functionality"""
    
    def test_document_post_process_success(self, db_session, sample_document):
        """Test successful document post-processing"""
        
        from app.models import Chunk, Summary, Task
        
        # Create processed chunks
        chunk1 = Chunk(
            id=str(uuid.uuid4()),
            doc_id=sample_document.id,
            page_no=1,
            chunk_no=1,
            text="This is chunk 1.",
            text_excerpt="This is chunk 1.",
            status="processed"
        )
        chunk2 = Chunk(
            id=str(uuid.uuid4()),
            doc_id=sample_document.id,
            page_no=1,
            chunk_no=2,
            text="This is chunk 2.",
            text_excerpt="This is chunk 2.",
            status="processed"
        )
        db_session.add_all([chunk1, chunk2])
        
        # Create some tasks
        task = Task(
            id=str(uuid.uuid4()),
            doc_id=sample_document.id,
            task_text="Test task",
            extracted_by="rule-based"
        )
        db_session.add(task)
        db_session.commit()
        
        # Mock summarizer service
        with patch('app.services.summarizer.summarizer_service') as mock_summarizer:
            mock_summarizer.summarize_text.return_value = "Chunk summary"
            mock_summarizer.hierarchical_summarize.return_value = "Document summary"
            
            # Post-process document
            result = document_post_process(sample_document.id)
            
            assert result['document_id'] == sample_document.id
            assert result['status'] == "processed"
            assert result['chunks_count'] == 2
            assert result['summary_generated'] == True
            assert result['processing_completed'] == True
            
            # Verify document was updated
            db_session.refresh(sample_document)
            assert sample_document.status == "processed"
            assert sample_document.is_processed == True
            assert sample_document.processed_at is not None
            
            # Verify summaries were created
            summaries = db_session.query(Summary).filter(Summary.doc_id == sample_document.id).all()
            assert len(summaries) >= 2  # At least chunk summaries + document summary
    
    def test_document_post_process_no_chunks(self, db_session, sample_document):
        """Test post-processing document with no processed chunks"""
        
        # Mock summarizer service
        with patch('app.services.summarizer.summarizer_service'):
            # Post-process document
            result = document_post_process(sample_document.id)
            
            assert result['document_id'] == sample_document.id
            assert result['status'] == "processed"
            assert result['chunks_count'] == 0
            
            # Verify document was still marked as processed
            db_session.refresh(sample_document)
            assert sample_document.status == "processed"
    
    def test_document_post_process_not_found(self, db_session):
        """Test post-processing non-existent document"""
        
        with pytest.raises(ValueError, match="Document .* not found"):
            document_post_process(99999)
    
    def test_generate_document_report(self, db_session, sample_document):
        """Test document report generation"""
        
        from app.models import Chunk, Summary, Task
        
        # Create test data
        chunk = Chunk(
            id=str(uuid.uuid4()),
            doc_id=sample_document.id,
            page_no=1,
            chunk_no=1,
            text="Test chunk",
            text_excerpt="Test chunk",
            status="processed",
            embedding_id="test-embedding-id",
            nlp_metadata={"entities": [{"text": "test", "label": "ORG"}]}
        )
        
        summary = Summary(
            id=str(uuid.uuid4()),
            doc_id=sample_document.id,
            level="DOCUMENT",
            text="Document summary",
            method="test"
        )
        
        task = Task(
            id=str(uuid.uuid4()),
            doc_id=sample_document.id,
            task_text="Test task",
            priority="high",
            status="open",
            extracted_by="rule-based"
        )
        
        db_session.add_all([chunk, summary, task])
        db_session.commit()
        
        from app.workers.post_processor import generate_document_report
        
        # Generate report
        report = generate_document_report(sample_document.id)
        
        assert report['document_id'] == sample_document.id
        assert report['document_title'] == sample_document.title
        assert report['summary'] == "Document summary"
        assert report['statistics']['total_chunks'] == 1
        assert report['statistics']['processed_chunks'] == 1
        assert report['statistics']['total_tasks'] == 1
        assert report['statistics']['has_embeddings'] == True
        assert len(report['chunks']) == 1
        assert len(report['tasks']) == 1


