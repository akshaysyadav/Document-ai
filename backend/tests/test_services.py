"""
Tests for service components
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from app.services.embedding import EmbeddingService
from app.services.summarizer import SummarizerService
from app.services.task_extractor import TaskExtractorService
from app.services.pdf_processor import PDFProcessorService


class TestEmbeddingService:
    """Test embedding service functionality"""
    
    def test_embedding_service_initialization(self):
        """Test embedding service initialization"""
        with patch('app.services.embedding.settings') as mock_settings:
            mock_settings.EMBEDDING_MODEL_NAME = "test-model"
            mock_settings.USE_OPENAI = False
            mock_settings.OPENAI_API_KEY = None
            
            with patch('sentence_transformers.SentenceTransformer'):
                service = EmbeddingService()
                assert service.model_name == "test-model"
                assert service.use_openai == False
    
    def test_generate_embedding(self):
        """Test single embedding generation"""
        with patch('app.services.embedding.settings') as mock_settings:
            mock_settings.USE_OPENAI = False
            
            service = EmbeddingService()
            with patch.object(service, '_generate_sentence_transformer_embedding') as mock_gen:
                mock_gen.return_value = [0.1] * 384
                
                result = service.generate_embedding("Test text")
                assert len(result) == 384
                assert all(isinstance(x, float) for x in result)
    
    def test_generate_embeddings_batch(self):
        """Test batch embedding generation"""
        with patch('app.services.embedding.settings') as mock_settings:
            mock_settings.USE_OPENAI = False
            
            service = EmbeddingService()
            with patch.object(service, '_generate_sentence_transformer_embeddings_batch') as mock_gen:
                mock_gen.return_value = [[0.1] * 384, [0.2] * 384]
                
                texts = ["Text 1", "Text 2"]
                result = service.generate_embeddings_batch(texts)
                assert len(result) == 2
                assert all(len(emb) == 384 for emb in result)
    
    def test_chunk_text_by_tokens(self):
        """Test text chunking functionality"""
        with patch('app.services.embedding.settings') as mock_settings:
            mock_settings.CHUNK_SIZE_TOKENS = 10
            mock_settings.CHUNK_OVERLAP_TOKENS = 2
            
            service = EmbeddingService()
            service.tokenizer = None  # Force character-based chunking
            
            text = "This is a test text that should be chunked into smaller pieces."
            chunks = service.chunk_text_by_tokens(text)
            
            assert len(chunks) > 0
            assert all(len(chunk) > 0 for chunk in chunks)
    
    def test_openai_embedding_fallback(self):
        """Test OpenAI embedding with API failure fallback"""
        with patch('app.services.embedding.settings') as mock_settings:
            mock_settings.USE_OPENAI = True
            mock_settings.OPENAI_API_KEY = "test-key"
            
            service = EmbeddingService()
            
            with patch('openai.Embedding.create') as mock_openai:
                mock_openai.side_effect = Exception("API Error")
                
                result = service.generate_embedding("Test text")
                # Should return dummy embedding on failure
                assert len(result) == 384
                assert all(x == 0.0 for x in result)


class TestSummarizerService:
    """Test summarization service functionality"""
    
    def test_summarizer_service_initialization(self):
        """Test summarizer service initialization"""
        with patch('app.services.summarizer.settings') as mock_settings:
            mock_settings.SUMMARIZER_MODEL_NAME = "test-model"
            mock_settings.USE_OPENAI = False
            mock_settings.OPENAI_API_KEY = None
            
            with patch('transformers.pipeline'):
                service = SummarizerService()
                assert service.model_name == "test-model"
                assert service.use_openai == False
    
    def test_summarize_text(self):
        """Test text summarization"""
        with patch('app.services.summarizer.settings') as mock_settings:
            mock_settings.USE_OPENAI = False
            
            service = SummarizerService()
            with patch.object(service, '_summarize_with_huggingface') as mock_summarize:
                mock_summarize.return_value = "This is a test summary."
                
                result = service.summarize_text("This is a long text that needs to be summarized.")
                assert result == "This is a test summary."
    
    def test_hierarchical_summarize(self):
        """Test hierarchical summarization"""
        with patch('app.services.summarizer.settings') as mock_settings:
            mock_settings.USE_OPENAI = False
            
            service = SummarizerService()
            with patch.object(service, 'summarize_text') as mock_summarize:
                mock_summarize.side_effect = [
                    "Chunk 1 summary",
                    "Chunk 2 summary", 
                    "Chunk 3 summary",
                    "Final summary"
                ]
                
                texts = ["Chunk 1", "Chunk 2", "Chunk 3"]
                result = service.hierarchical_summarize(texts)
                assert result == "Final summary"
                assert mock_summarize.call_count == 4
    
    def test_extractive_summary_fallback(self):
        """Test extractive summary fallback"""
        with patch('app.services.summarizer.settings') as mock_settings:
            mock_settings.USE_OPENAI = False
            
            service = SummarizerService()
            service.summarizer_pipeline = None
            service.model = None
            service.tokenizer = None
            
            text = "This is sentence one. This is sentence two. This is sentence three."
            result = service.summarize_text(text)
            
            # Should use extractive summary fallback
            assert len(result) > 0
            assert result in text


class TestTaskExtractorService:
    """Test task extraction service functionality"""
    
    def test_task_extractor_service_initialization(self):
        """Test task extractor service initialization"""
        with patch('app.services.task_extractor.settings') as mock_settings:
            mock_settings.USE_OPENAI = False
            mock_settings.OPENAI_API_KEY = None
            mock_settings.TASK_EXTRACTOR_MODEL = None
            
            service = TaskExtractorService()
            assert service.use_openai == False
    
    def test_extract_tasks_rule_based(self):
        """Test rule-based task extraction"""
        with patch('app.services.task_extractor.settings') as mock_settings:
            mock_settings.USE_OPENAI = False
            
            service = TaskExtractorService()
            
            text = "Action: Please review this document. Task: Update the report by Friday."
            tasks = service.extract_tasks(text, doc_id=1)
            
            assert len(tasks) > 0
            assert all('task_text' in task for task in tasks)
            assert all('doc_id' in task for task in tasks)
    
    def test_extract_tasks_with_assignee(self):
        """Test task extraction with assignee detection"""
        with patch('app.services.task_extractor.settings') as mock_settings:
            mock_settings.USE_OPENAI = False
            
            service = TaskExtractorService()
            
            text = "John should review the document and provide feedback."
            tasks = service.extract_tasks(text, doc_id=1)
            
            # Should detect "John" as assignee
            john_tasks = [task for task in tasks if task.get('assignee') == 'John']
            assert len(john_tasks) > 0
    
    def test_extract_tasks_with_due_date(self):
        """Test task extraction with due date detection"""
        with patch('app.services.task_extractor.settings') as mock_settings:
            mock_settings.USE_OPENAI = False
            
            service = TaskExtractorService()
            
            text = "Please complete this task by January 15, 2024."
            tasks = service.extract_tasks(text, doc_id=1)
            
            # Should detect due date
            tasks_with_dates = [task for task in tasks if task.get('due_date') is not None]
            assert len(tasks_with_dates) > 0
    
    def test_llm_task_extraction(self):
        """Test LLM-based task extraction"""
        with patch('app.services.task_extractor.settings') as mock_settings:
            mock_settings.USE_OPENAI = True
            mock_settings.OPENAI_API_KEY = "test-key"
            
            service = TaskExtractorService()
            
            with patch('openai.ChatCompletion.create') as mock_openai:
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = '[{"task_text": "Test task", "assignee": null, "due_date": null, "priority": "medium", "confidence": 0.8}]'
                mock_openai.return_value = mock_response
                
                text = "Please complete the following tasks: 1. Review document 2. Send feedback"
                tasks = service.extract_tasks(text, doc_id=1)
                
                # Should include LLM-extracted tasks
                llm_tasks = [task for task in tasks if task.get('extracted_by') == 'llm']
                assert len(llm_tasks) > 0
    
    def test_deduplicate_tasks(self):
        """Test task deduplication"""
        with patch('app.services.task_extractor.settings') as mock_settings:
            mock_settings.USE_OPENAI = False
            
            service = TaskExtractorService()
            
            tasks = [
                {'task_text': 'Review document', 'doc_id': 1, 'source_chunk_id': None, 'assignee': None, 'due_date': None, 'priority': 'medium', 'status': 'open', 'extracted_by': 'rule-based', 'metadata': {}},
                {'task_text': 'Review document', 'doc_id': 1, 'source_chunk_id': None, 'assignee': None, 'due_date': None, 'priority': 'high', 'status': 'open', 'extracted_by': 'llm', 'metadata': {}},
                {'task_text': 'Update report', 'doc_id': 1, 'source_chunk_id': None, 'assignee': None, 'due_date': None, 'priority': 'medium', 'status': 'open', 'extracted_by': 'rule-based', 'metadata': {}}
            ]
            
            deduplicated = service._deduplicate_tasks(tasks)
            assert len(deduplicated) == 2  # Should remove duplicate "Review document"


class TestPDFProcessorService:
    """Test PDF processing service functionality"""
    
    def test_pdf_processor_service_initialization(self):
        """Test PDF processor service initialization"""
        service = PDFProcessorService()
        assert service.ocr_enabled == True
    
    def test_extract_text_from_pdf(self):
        """Test PDF text extraction"""
        service = PDFProcessorService()
        
        # Mock PDF bytes (minimal PDF structure)
        pdf_bytes = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Hello World) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
299
%%EOF"""
        
        with patch('pdfplumber.open') as mock_pdfplumber:
            mock_page = Mock()
            mock_page.extract_text.return_value = "Hello World"
            mock_pdf = Mock()
            mock_pdf.pages = [mock_page]
            mock_pdfplumber.return_value.__enter__.return_value = mock_pdf
            
            result = service.extract_text_from_pdf(pdf_bytes)
            
            assert result['success'] == True
            assert result['total_pages'] == 1
            assert len(result['pages']) == 1
            assert result['pages'][0]['text'] == "Hello World"
    
    def test_extract_text_fallback_to_pypdf2(self):
        """Test fallback to PyPDF2 when pdfplumber fails"""
        service = PDFProcessorService()
        
        pdf_bytes = b"invalid pdf content"
        
        with patch('pdfplumber.open') as mock_pdfplumber:
            mock_pdfplumber.side_effect = Exception("pdfplumber failed")
            
            with patch('PyPDF2.PdfReader') as mock_pypdf2:
                mock_page = Mock()
                mock_page.extract_text.return_value = "Fallback text"
                mock_reader = Mock()
                mock_reader.pages = [mock_page]
                mock_pypdf2.return_value = mock_reader
                
                result = service.extract_text_from_pdf(pdf_bytes)
                
                assert result['success'] == True
                assert result['extraction_method'] == 'pypdf2'
                assert result['pages'][0]['text'] == "Fallback text"
    
    def test_get_page_text(self):
        """Test getting text from specific page"""
        service = PDFProcessorService()
        
        pdf_bytes = b"test pdf"
        
        with patch.object(service, 'extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = {
                'success': True,
                'pages': [
                    {'page_number': 1, 'text': 'Page 1 text'},
                    {'page_number': 2, 'text': 'Page 2 text'}
                ]
            }
            
            result = service.get_page_text(pdf_bytes, 2)
            assert result == "Page 2 text"
            
            result = service.get_page_text(pdf_bytes, 5)
            assert result is None  # Page doesn't exist


