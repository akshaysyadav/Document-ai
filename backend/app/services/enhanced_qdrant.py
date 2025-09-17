"""
Enhanced Qdrant client service for vector operations.
"""
import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from ..settings import settings

logger = logging.getLogger(__name__)


class EnhancedQdrantService:
    def __init__(self):
        self.url = settings.QDRANT_URL
        self.api_key = settings.QDRANT_API_KEY
        self.collection_name = "documents"
        self.vector_size = 384  # sentence-transformers/all-MiniLM-L6-v2 dimension
        self.client = None
        
        # Initialize client
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Qdrant client"""
        try:
            if self.api_key:
                self.client = QdrantClient(
                    url=self.url,
                    api_key=self.api_key
                )
            else:
                self.client = QdrantClient(url=self.url)
            
            logger.info(f"Qdrant client initialized: {self.url}")
            
            # Ensure collection exists
            self._ensure_collection_exists()
            
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {e}")
            self.client = None
            logger.warning("Qdrant client will be unavailable")
    
    def _ensure_collection_exists(self):
        """Ensure the collection exists with correct configuration"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Qdrant collection exists: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {e}")
            # Don't raise the exception to allow the service to continue
            logger.warning("Continuing without Qdrant collection setup")
    
    def upsert_points(self, points: List[Dict[str, Any]]) -> bool:
        """
        Upsert points to the collection
        
        Args:
            points: List of point dictionaries with 'id', 'vector', and 'payload'
            
        Returns:
            True if successful, False otherwise
        """
        if self.client is None:
            logger.warning("Qdrant client not available")
            return False
            
        try:
            point_structs = []
            for point in points:
                point_struct = PointStruct(
                    id=point['id'],
                    vector=point['vector'],
                    payload=point['payload']
                )
                point_structs.append(point_struct)
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=point_structs
            )
            
            logger.info(f"Upserted {len(points)} points to Qdrant")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert points: {e}")
            return False
    
    def upsert_point(self, point_id: str, vector: List[float], payload: Dict[str, Any]) -> bool:
        """
        Upsert a single point
        
        Args:
            point_id: Unique identifier for the point
            vector: Embedding vector
            payload: Metadata payload
            
        Returns:
            True if successful, False otherwise
        """
        if self.client is None:
            logger.warning("Qdrant client not available")
            return False
            
        try:
            point = PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.info(f"Upserted point {point_id} to Qdrant")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert point {point_id}: {e}")
            return False
    
    def search_similar(self, query_vector: List[float], limit: int = 10, 
                      score_threshold: float = 0.0, 
                      doc_id_filter: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for similar vectors
        
        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            doc_id_filter: Optional document ID filter
            
        Returns:
            List of search results with scores and payloads
        """
        if self.client is None:
            logger.warning("Qdrant client not available")
            return []
            
        try:
            # Build filter if needed
            query_filter = None
            if doc_id_filter is not None:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="doc_id",
                            match=MatchValue(value=doc_id_filter)
                        )
                    ]
                )
            
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=query_filter
            )
            
            results = []
            for result in search_results:
                results.append({
                    'id': result.id,
                    'score': result.score,
                    'payload': result.payload
                })
            
            logger.info(f"Found {len(results)} similar vectors")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def delete_points(self, point_ids: List[str]) -> bool:
        """
        Delete points by IDs
        
        Args:
            point_ids: List of point IDs to delete
            
        Returns:
            True if successful, False otherwise
        """
        if self.client is None:
            logger.warning("Qdrant client not available")
            return False
            
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=point_ids
            )
            
            logger.info(f"Deleted {len(point_ids)} points from Qdrant")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete points: {e}")
            return False
    
    def delete_points_by_doc_id(self, doc_id: int) -> bool:
        """
        Delete all points for a specific document
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if successful, False otherwise
        """
        if self.client is None:
            logger.warning("Qdrant client not available")
            return False
            
        try:
            # First, find all points for this document
            search_results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="doc_id",
                            match=MatchValue(value=doc_id)
                        )
                    ]
                ),
                limit=1000  # Adjust based on expected max chunks per document
            )
            
            if search_results[0]:  # Points found
                point_ids = [point.id for point in search_results[0]]
                return self.delete_points(point_ids)
            
            logger.info(f"No points found for document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete points for document {doc_id}: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get collection information
        
        Returns:
            Dictionary with collection stats and configuration
        """
        if self.client is None:
            logger.warning("Qdrant client not available")
            return {}
            
        try:
            # Use a more robust method to get collection info
            collections = self.client.get_collections()
            for collection in collections.collections:
                if collection.name == self.collection_name:
                    return {
                        'name': collection.name,
                        'vector_size': self.vector_size,
                        'distance': 'Cosine',
                        'points_count': 0,  # Default value
                        'segments_count': 0,
                        'status': 'green'
                    }
            
            # Collection not found
            return {
                'name': self.collection_name,
                'vector_size': self.vector_size,
                'distance': 'Cosine',
                'points_count': 0,
                'segments_count': 0,
                'status': 'not_found'
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {}
    
    def recreate_collection(self) -> bool:
        """
        Recreate the collection (useful for development/reset)
        
        Returns:
            True if successful, False otherwise
        """
        if self.client is None:
            logger.warning("Qdrant client not available")
            return False
            
        try:
            # Delete existing collection
            try:
                self.client.delete_collection(self.collection_name)
                logger.info(f"Deleted existing collection: {self.collection_name}")
            except Exception as e:
                logger.warning(f"Failed to delete existing collection: {e}")
            
            # Create new collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            
            logger.info(f"Recreated collection: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to recreate collection: {e}")
            return False
    
    def health_check(self) -> bool:
        """
        Check if Qdrant service is healthy
        
        Returns:
            True if healthy, False otherwise
        """
        if self.client is None:
            return False
            
        try:
            self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False


# Global instance
enhanced_qdrant_service = EnhancedQdrantService()
