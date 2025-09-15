from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import os
import logging

logger = logging.getLogger(__name__)

# Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

# Initialize Qdrant client
try:
    qdrant_client = QdrantClient(url=QDRANT_URL)
    logger.info(f"Qdrant client initialized with URL: {QDRANT_URL}")
except Exception as e:
    logger.error(f"Failed to initialize Qdrant client: {e}")
    qdrant_client = None

# Collection configuration
COLLECTION_NAME = "kmrl_documents"
VECTOR_SIZE = 768  # Standard BERT embedding size

def create_collection(collection_name: str = COLLECTION_NAME, vector_size: int = VECTOR_SIZE):
    """Create a new collection in Qdrant"""
    try:
        if qdrant_client is None:
            raise Exception("Qdrant client not initialized")
            
        # Check if collection exists
        collections = qdrant_client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if collection_name not in collection_names:
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
            logger.info(f"Created Qdrant collection: {collection_name}")
        else:
            logger.info(f"Qdrant collection already exists: {collection_name}")
            
    except Exception as e:
        logger.error(f"Failed to create Qdrant collection: {e}")
        raise

def add_document_vector(document_id: str, vector: list, metadata: dict = None):
    """Add a document vector to Qdrant"""
    try:
        if qdrant_client is None:
            raise Exception("Qdrant client not initialized")
            
        point = PointStruct(
            id=document_id,
            vector=vector,
            payload=metadata or {}
        )
        
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[point]
        )
        
        logger.info(f"Added vector for document: {document_id}")
        
    except Exception as e:
        logger.error(f"Failed to add document vector: {e}")
        raise

def search_similar_documents(query_vector: list, limit: int = 10):
    """Search for similar documents using vector similarity"""
    try:
        if qdrant_client is None:
            raise Exception("Qdrant client not initialized")
            
        search_result = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit
        )
        
        return search_result
        
    except Exception as e:
        logger.error(f"Failed to search documents: {e}")
        raise

# Initialize collection on module import
if qdrant_client:
    try:
        create_collection()
    except Exception as e:
        logger.warning(f"Could not create collection on startup: {e}")
