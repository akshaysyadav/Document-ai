"""
End-to-end tests for the document processing pipeline
"""
import pytest
import io
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient


class TestEndToEndDocumentProcessing:
    """Test the complete document processing pipeline"""
    
    def test_upload_and_process_document(
        self, 
        client: TestClient, 
        sample_pdf_bytes: bytes,
        mock_minio,
        mock_qdrant,
        mock_embedding_service,
        mock_summarizer_service,
        mock_task_extractor_service,
        db_session
    ):
        """Test complete document upload and processing workflow"""
        
        # Mock MinIO file operations
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
                        'text': 'This is a test document with some content. Please review this document and provide feedback.',
                        'confidence': 0.95,
                        'extraction_method': 'test'
                    }
                ],
                'total_pages': 1,
                'extraction_method': 'test',
                'success': True,
                'error': None
            }
            
            # Upload document
            files = {"file": ("test.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")}
            data = {
                "title": "Test Document",
                "description": "A test document for end-to-end testing",
                "tags": "test, document, pdf"
            }
            
            response = client.post("/api/documents/", files=files, data=data)
            assert response.status_code == 200
            
            document_data = response.json()
            doc_id = document_data["id"]
            assert document_data["title"] == "Test Document"
            assert document_data["status"] == "uploaded"
            
            # Mock background processing
            with patch('app.workers.enqueue_document_processing') as mock_enqueue:
                # Simulate processing completion
                from app.workers.document_processor import process_document
                from app.workers.chunk_processor import process_chunk
                from app.workers.post_processor import document_post_process
                
                # Process document
                process_result = process_document(doc_id)
                assert process_result["document_id"] == doc_id
                assert process_result["status"] == "processing_enqueued"
                
                # Check that chunks were created
                from app.models import Chunk
                chunks = db_session.query(Chunk).filter(Chunk.doc_id == doc_id).all()
                assert len(chunks) > 0
                
                # Process chunks
                for chunk in chunks:
                    chunk_result = process_chunk(chunk.id)
                    assert chunk_result["status"] == "processed"
                
                # Post-process document
                post_process_result = document_post_process(doc_id)
                assert post_process_result["status"] == "processed"
                
                # Check final results
                response = client.get(f"/api/documents/{doc_id}/results")
                assert response.status_code == 200
                
                results = response.json()
                assert results["doc_id"] == doc_id
                assert results["status"] == "processed"
                assert len(results["chunks"]) > 0
                assert results["summary"] is not None
                assert len(results["tasks"]) > 0
    
    def test_document_reprocessing(self, client: TestClient, sample_document, db_session):
        """Test document reprocessing functionality"""
        
        # Initially mark as processed
        sample_document.status = "processed"
        sample_document.is_processed = True
        db_session.commit()
        
        # Reprocess document
        with patch('app.workers.enqueue_document_processing') as mock_enqueue:
            response = client.post(f"/api/documents/{sample_document.id}/reprocess")
            assert response.status_code == 200
            
            # Check that document status was reset
            db_session.refresh(sample_document)
            assert sample_document.status == "uploaded"
            assert sample_document.is_processed == False
            
            # Verify enqueue was called
            mock_enqueue.assert_called_once_with(sample_document.id)
    
    def test_get_document_results(self, client: TestClient, sample_document, sample_chunk, sample_task, sample_summary):
        """Test getting comprehensive document results"""
        
        response = client.get(f"/api/documents/{sample_document.id}/results")
        assert response.status_code == 200
        
        results = response.json()
        assert results["doc_id"] == sample_document.id
        assert results["title"] == sample_document.title
        assert results["summary"] == sample_summary.text
        assert len(results["chunks"]) == 1
        assert len(results["tasks"]) == 1
        assert results["status"] == sample_document.status
    
    def test_get_document_chunks(self, client: TestClient, sample_document, sample_chunk):
        """Test getting document chunks"""
        
        response = client.get(f"/api/documents/{sample_document.id}/chunks")
        assert response.status_code == 200
        
        chunks = response.json()
        assert len(chunks) == 1
        assert chunks[0]["id"] == sample_chunk.id
        assert chunks[0]["doc_id"] == sample_document.id
        assert chunks[0]["text_excerpt"] == sample_chunk.text_excerpt
    
    def test_get_document_tasks(self, client: TestClient, sample_document, sample_task):
        """Test getting document tasks"""
        
        response = client.get(f"/api/documents/{sample_document.id}/tasks")
        assert response.status_code == 200
        
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["id"] == sample_task.id
        assert tasks[0]["doc_id"] == sample_document.id
        assert tasks[0]["task_text"] == sample_task.task_text
    
    def test_update_task(self, client: TestClient, sample_task):
        """Test updating a task"""
        
        update_data = {
            "assignee": "Jane Doe",
            "priority": "high",
            "status": "in-progress"
        }
        
        response = client.patch(f"/api/documents/tasks/{sample_task.id}", json=update_data)
        assert response.status_code == 200
        
        updated_task = response.json()
        assert updated_task["assignee"] == "Jane Doe"
        assert updated_task["priority"] == "high"
        assert updated_task["status"] == "in-progress"
    
    def test_get_document_report(self, client: TestClient, sample_document):
        """Test getting detailed document report"""
        
        with patch('app.workers.post_processor.generate_document_report') as mock_report:
            mock_report.return_value = {
                "document_id": sample_document.id,
                "document_title": sample_document.title,
                "document_status": sample_document.status,
                "statistics": {
                    "total_chunks": 1,
                    "processed_chunks": 1,
                    "total_tasks": 1,
                    "has_embeddings": True
                }
            }
            
            response = client.get(f"/api/documents/{sample_document.id}/report")
            assert response.status_code == 200
            
            report = response.json()
            assert report["document_id"] == sample_document.id
            assert "statistics" in report
    
    def test_document_not_found(self, client: TestClient):
        """Test handling of non-existent documents"""
        
        response = client.get("/api/documents/99999/results")
        assert response.status_code == 404
        
        response = client.get("/api/documents/99999/chunks")
        assert response.status_code == 404
        
        response = client.get("/api/documents/99999/tasks")
        assert response.status_code == 404
        
        response = client.post("/api/documents/99999/reprocess")
        assert response.status_code == 404
    
    def test_task_not_found(self, client: TestClient):
        """Test handling of non-existent tasks"""
        
        update_data = {"status": "done"}
        response = client.patch("/api/documents/tasks/non-existent-id", json=update_data)
        assert response.status_code == 404



