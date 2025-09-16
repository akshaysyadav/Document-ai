"""
Embedding service for generating text embeddings using various models.
Supports sentence-transformers and OpenAI embeddings with fallbacks.
"""
import logging
import numpy as np
from typing import List, Optional
import tiktoken
from sentence_transformers import SentenceTransformer
import openai
from ..settings import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL_NAME
        self.use_openai = settings.USE_OPENAI
        self.openai_api_key = settings.OPENAI_API_KEY
        self.model = None
        self.tokenizer = None
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize embedding models"""
        try:
            if self.use_openai and self.openai_api_key:
                openai.api_key = self.openai_api_key
                logger.info("OpenAI embedding service initialized")
            else:
                # Load sentence-transformers model
                self.model = SentenceTransformer(self.model_name)
                logger.info(f"Sentence-transformers model loaded: {self.model_name}")
                
                # Try to load tokenizer for the model
                try:
                    self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")  # Fallback tokenizer
                except:
                    logger.warning("Could not load tiktoken tokenizer, using character-based chunking")
                    
        except Exception as e:
            logger.error(f"Failed to initialize embedding models: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text
            
        Returns:
            List of floats representing the embedding
        """
        try:
            if self.use_openai and self.openai_api_key:
                return self._generate_openai_embedding(text)
            else:
                return self._generate_sentence_transformer_embedding(text)
                
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            # Return dummy embedding as fallback
            return [0.0] * 384
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (more efficient for batch processing)
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embeddings
        """
        try:
            if self.use_openai and self.openai_api_key:
                return self._generate_openai_embeddings_batch(texts)
            else:
                return self._generate_sentence_transformer_embeddings_batch(texts)
                
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            # Return dummy embeddings as fallback
            return [[0.0] * 384 for _ in texts]
    
    def _generate_openai_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI API"""
        try:
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response['data'][0]['embedding']
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            raise
    
    def _generate_openai_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API in batch"""
        try:
            # OpenAI has a limit on batch size
            batch_size = 100
            embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = openai.Embedding.create(
                    input=batch,
                    model="text-embedding-ada-002"
                )
                batch_embeddings = [item['embedding'] for item in response['data']]
                embeddings.extend(batch_embeddings)
            
            return embeddings
        except Exception as e:
            logger.error(f"OpenAI batch embedding failed: {e}")
            raise
    
    def _generate_sentence_transformer_embedding(self, text: str) -> List[float]:
        """Generate embedding using sentence-transformers"""
        try:
            if self.model is None:
                raise Exception("Sentence-transformer model not loaded")
            
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Sentence-transformer embedding failed: {e}")
            raise
    
    def _generate_sentence_transformer_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using sentence-transformers in batch"""
        try:
            if self.model is None:
                raise Exception("Sentence-transformer model not loaded")
            
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Sentence-transformer batch embedding failed: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by the current model"""
        if self.use_openai and self.openai_api_key:
            return 1536  # OpenAI text-embedding-ada-002 dimension
        else:
            return 384  # sentence-transformers/all-MiniLM-L6-v2 dimension
    
    def chunk_text_by_tokens(self, text: str, chunk_size_tokens: int = None, overlap_tokens: int = None) -> List[str]:
        """
        Split text into chunks based on token count
        
        Args:
            text: Input text to chunk
            chunk_size_tokens: Maximum tokens per chunk (default from settings)
            overlap_tokens: Overlap tokens between chunks (default from settings)
            
        Returns:
            List of text chunks
        """
        if chunk_size_tokens is None:
            chunk_size_tokens = settings.CHUNK_SIZE_TOKENS
        if overlap_tokens is None:
            overlap_tokens = settings.CHUNK_OVERLAP_TOKENS
        
        try:
            if self.tokenizer:
                return self._chunk_by_tiktoken(text, chunk_size_tokens, overlap_tokens)
            else:
                return self._chunk_by_characters(text, chunk_size_tokens, overlap_tokens)
        except Exception as e:
            logger.error(f"Token-based chunking failed, falling back to character-based: {e}")
            return self._chunk_by_characters(text, chunk_size_tokens, overlap_tokens)
    
    def _chunk_by_tiktoken(self, text: str, chunk_size_tokens: int, overlap_tokens: int) -> List[str]:
        """Chunk text using tiktoken tokenizer"""
        tokens = self.tokenizer.encode(text)
        chunks = []
        
        for i in range(0, len(tokens), chunk_size_tokens - overlap_tokens):
            chunk_tokens = tokens[i:i + chunk_size_tokens]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            # Stop if we've covered all tokens
            if i + chunk_size_tokens >= len(tokens):
                break
        
        return chunks
    
    def _chunk_by_characters(self, text: str, chunk_size_tokens: int, overlap_tokens: int) -> List[str]:
        """Fallback chunking by characters (rough approximation)"""
        # Rough approximation: 1 token ≈ 4 characters for English text
        char_size = chunk_size_tokens * 4
        char_overlap = overlap_tokens * 4
        
        chunks = []
        for i in range(0, len(text), char_size - char_overlap):
            chunk = text[i:i + char_size]
            chunks.append(chunk)
            
            if i + char_size >= len(text):
                break
        
        return chunks


# Global instance
embedding_service = EmbeddingService()

