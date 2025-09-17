"""
Test configuration and fixtures
"""
import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"  # Use different Redis DB for tests
os.environ["QDRANT_URL"] = "http://localhost:6333"
os.environ["MINIO_ENDPOINT"] = "localhost:9000"

from app.main import app
from app.database import get_db, Base
from app.models import Document, Chunk, Summary, Task


# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_session():
    """Create test database session"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create test client with database dependency override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_document(db_session):
    """Create a sample document for testing"""
    document = Document(
        title="Test Document",
        description="A test document for unit testing",
        content="This is test content for the document.",
        file_path="test/sample.pdf",
        file_name="sample.pdf",
        file_size=1024,
        file_type="application/pdf",
        status="uploaded"
    )
    
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)
    
    return document


@pytest.fixture
def sample_chunk(db_session, sample_document):
    """Create a sample chunk for testing"""
    chunk = Chunk(
        id="test-chunk-1",
        doc_id=sample_document.id,
        page_no=1,
        chunk_no=1,
        text="This is a test chunk with some content for testing purposes.",
        text_excerpt="This is a test chunk with some content...",
        status="processed",
        embedding_dim=384
    )
    
    db_session.add(chunk)
    db_session.commit()
    db_session.refresh(chunk)
    
    return chunk


@pytest.fixture
def sample_task(db_session, sample_document):
    """Create a sample task for testing"""
    task = Task(
        id="test-task-1",
        doc_id=sample_document.id,
        task_text="Please review the document and provide feedback",
        assignee="John Doe",
        priority="medium",
        status="open",
        extracted_by="rule-based"
    )
    
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    
    return task


@pytest.fixture
def sample_summary(db_session, sample_document):
    """Create a sample summary for testing"""
    summary = Summary(
        id="test-summary-1",
        doc_id=sample_document.id,
        level="DOCUMENT",
        text="This is a test summary of the document.",
        method="test-method"
    )
    
    db_session.add(summary)
    db_session.commit()
    db_session.refresh(summary)
    
    return summary


@pytest.fixture
def mock_minio():
    """Mock MinIO client"""
    with patch('app.database.minio_client') as mock:
        mock.bucket_exists.return_value = True
        mock.get_object.return_value = Mock()
        mock.put_object.return_value = True
        yield mock


@pytest.fixture
def mock_qdrant():
    """Mock Qdrant client"""
    with patch('app.services.enhanced_qdrant.enhanced_qdrant_service') as mock:
        mock.upsert_point.return_value = True
        mock.search_similar.return_value = []
        mock.health_check.return_value = True
        yield mock


@pytest.fixture
def mock_embedding_service():
    """Mock embedding service"""
    with patch('app.services.embedding.embedding_service') as mock:
        mock.generate_embedding.return_value = [0.1] * 384
        mock.generate_embeddings_batch.return_value = [[0.1] * 384] * 5
        mock.chunk_text_by_tokens.return_value = [
            "This is chunk 1",
            "This is chunk 2",
            "This is chunk 3"
        ]
        yield mock


@pytest.fixture
def mock_summarizer_service():
    """Mock summarizer service"""
    with patch('app.services.summarizer.summarizer_service') as mock:
        mock.summarize_text.return_value = "This is a test summary"
        mock.hierarchical_summarize.return_value = "This is a hierarchical summary"
        yield mock


@pytest.fixture
def mock_task_extractor_service():
    """Mock task extractor service"""
    with patch('app.services.task_extractor.task_extractor_service') as mock:
        mock.extract_tasks.return_value = [
            {
                'task_text': 'Test task 1',
                'doc_id': 1,
                'source_chunk_id': 'test-chunk-1',
                'assignee': None,
                'due_date': None,
                'priority': 'medium',
                'status': 'open',
                'extracted_by': 'rule-based',
                'metadata': {}
            }
        ]
        yield mock


@pytest.fixture
def sample_pdf_bytes():
    """Create sample PDF bytes for testing"""
    # This is a minimal PDF structure for testing
    pdf_content = b"""%PDF-1.4
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
    
    return pdf_content


