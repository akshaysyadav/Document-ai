import logging
import numpy as np
from typing import List, Dict, Any
import spacy
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Initialize models
try:
    # Load spaCy model for NER
    nlp_model = spacy.load("en_core_web_sm")
    logger.info("✅ spaCy model loaded successfully")
except OSError:
    logger.warning("⚠️ spaCy model not found, using fallback NER")
    nlp_model = None

try:
    # Load sentence transformer for embeddings
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("✅ SentenceTransformer model loaded successfully")
except Exception as e:
    logger.warning(f"⚠️ SentenceTransformer model failed to load: {e}")
    embedding_model = None

def generate_embeddings(text: str) -> List[float]:
    """Generate embeddings for text using SentenceTransformer"""
    try:
        if embedding_model is None:
            # Fallback: simple word-based embedding
            return _generate_simple_embeddings(text)
        
        # Generate embeddings
        embeddings = embedding_model.encode(text)
        return embeddings.tolist()
        
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        return _generate_simple_embeddings(text)

def _generate_simple_embeddings(text: str, dimension: int = 384) -> List[float]:
    """Simple fallback embedding generation"""
    try:
        # Simple hash-based embedding
        words = text.lower().split()
        embedding = [0.0] * dimension
        
        for i, word in enumerate(words[:dimension]):
            # Simple hash-based feature
            hash_val = hash(word) % dimension
            embedding[hash_val] += 1.0
        
        # Normalize
        norm = sum(x*x for x in embedding) ** 0.5
        if norm > 0:
            embedding = [x/norm for x in embedding]
        
        return embedding
    except Exception as e:
        logger.error(f"Failed to generate simple embeddings: {e}")
        return [0.0] * dimension

def extract_entities(text: str) -> List[Dict[str, str]]:
    """Extract named entities from text"""
    try:
        if nlp_model is None:
            return _extract_simple_entities(text)
        
        doc = nlp_model(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        
        return entities
        
    except Exception as e:
        logger.error(f"Failed to extract entities: {e}")
        return _extract_simple_entities(text)

def _extract_simple_entities(text: str) -> List[Dict[str, str]]:
    """Simple entity extraction fallback"""
    entities = []
    
    # Simple keyword-based entity extraction
    keywords = {
        'PERSON': ['john', 'mary', 'smith', 'jones', 'brown', 'davis', 'wilson', 'miller'],
        'ORG': ['company', 'corp', 'inc', 'ltd', 'organization', 'department', 'ministry'],
        'GPE': ['city', 'state', 'country', 'nation', 'government', 'federal'],
        'MONEY': ['dollar', 'euro', 'pound', 'rupee', 'yen', '$', '€', '£', '₹'],
        'DATE': ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
    }
    
    words = text.lower().split()
    for i, word in enumerate(words):
        for label, keyword_list in keywords.items():
            if word in keyword_list:
                entities.append({
                    "text": word,
                    "label": label,
                    "start": i,
                    "end": i + 1
                })
    
    return entities

def generate_summary(text: str, max_sentences: int = 3) -> str:
    """Generate extractive summary of text"""
    try:
        sentences = text.split('. ')
        if len(sentences) <= max_sentences:
            return text
        
        # Simple extractive summary - take first few sentences
        summary_sentences = sentences[:max_sentences]
        summary = '. '.join(summary_sentences)
        
        # Ensure it ends with a period
        if not summary.endswith('.'):
            summary += '.'
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to generate summary: {e}")
        return text[:500] + "..." if len(text) > 500 else text

def extract_tasks(text: str) -> List[Dict[str, Any]]:
    """Extract actionable tasks from text"""
    try:
        tasks = []
        
        # Task extraction keywords
        task_patterns = [
            'need to', 'must', 'should', 'required to', 'task is', 'action item',
            'todo', 'implement', 'create', 'build', 'develop', 'install',
            'configure', 'setup', 'update', 'fix', 'resolve', 'check',
            'verify', 'test', 'review', 'approve', 'submit', 'send'
        ]
        
        sentences = text.split('. ')
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if sentence contains task patterns
            if any(pattern in sentence.lower() for pattern in task_patterns):
                # Determine priority
                priority = 'medium'
                if any(word in sentence.lower() for word in ['urgent', 'critical', 'immediate', 'asap', 'emergency']):
                    priority = 'high'
                elif any(word in sentence.lower() for word in ['optional', 'nice to have', 'later', 'low priority']):
                    priority = 'low'
                
                tasks.append({
                    "text": sentence,
                    "priority": priority,
                    "status": "open"
                })
        
        return tasks
        
    except Exception as e:
        logger.error(f"Failed to extract tasks: {e}")
        return []