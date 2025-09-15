import spacy
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("spaCy English model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load spaCy model: {e}")
    nlp = None

# Load HuggingFace model for embeddings
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModel.from_pretrained(MODEL_NAME)
    logger.info(f"HuggingFace model loaded: {MODEL_NAME}")
except Exception as e:
    logger.error(f"Failed to load HuggingFace model: {e}")
    tokenizer = None
    model = None

def generate_embeddings(text: str) -> List[float]:
    """
    Generate text embeddings using HuggingFace transformers
    
    Args:
        text (str): Input text
        
    Returns:
        List[float]: Text embeddings
    """
    try:
        if tokenizer is None or model is None:
            raise Exception("HuggingFace model not loaded")
            
        logger.info(f"Generating embeddings for text of length: {len(text)}")
        
        # Tokenize and encode
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        
        # Generate embeddings
        with torch.no_grad():
            outputs = model(**inputs)
            
        # Use CLS token embedding or mean pooling
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
        
        logger.info(f"Generated embeddings of size: {len(embeddings)}")
        return embeddings.tolist()
        
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        # Return dummy embeddings for now
        return [0.0] * 384

def extract_entities(text: str) -> List[Dict[str, Any]]:
    """
    Extract named entities from text using spaCy
    
    Args:
        text (str): Input text
        
    Returns:
        List[Dict]: List of extracted entities
    """
    try:
        if nlp is None:
            raise Exception("spaCy model not loaded")
            
        logger.info(f"Extracting entities from text of length: {len(text)}")
        
        # Process text
        doc = nlp(text)
        
        # Extract entities
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "description": spacy.explain(ent.label_)
            })
            
        logger.info(f"Extracted {len(entities)} entities")
        return entities
        
    except Exception as e:
        logger.error(f"Failed to extract entities: {e}")
        return []

def extract_keywords(text: str, num_keywords: int = 10) -> List[Dict[str, Any]]:
    """
    Extract keywords from text using spaCy
    
    Args:
        text (str): Input text
        num_keywords (int): Number of keywords to extract
        
    Returns:
        List[Dict]: List of keywords with scores
    """
    try:
        if nlp is None:
            raise Exception("spaCy model not loaded")
            
        logger.info(f"Extracting keywords from text of length: {len(text)}")
        
        # Process text
        doc = nlp(text)
        
        # Extract keywords (simplified approach)
        keywords = []
        word_freq = {}
        
        for token in doc:
            if (not token.is_stop and 
                not token.is_punct and 
                not token.is_space and 
                len(token.text) > 2 and
                token.pos_ in ['NOUN', 'ADJ', 'VERB']):
                
                word = token.lemma_.lower()
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and take top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        for word, freq in sorted_words[:num_keywords]:
            keywords.append({
                "word": word,
                "frequency": freq,
                "score": freq / len(doc)
            })
            
        logger.info(f"Extracted {len(keywords)} keywords")
        return keywords
        
    except Exception as e:
        logger.error(f"Failed to extract keywords: {e}")
        return []

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze text sentiment (placeholder for future implementation)
    
    Args:
        text (str): Input text
        
    Returns:
        Dict: Sentiment analysis results
    """
    logger.warning("Sentiment analysis not implemented yet")
    return {
        "sentiment": "neutral",
        "confidence": 0.5,
        "positive": 0.33,
        "negative": 0.33,
        "neutral": 0.34
    }

def summarize_text(text: str, max_length: int = 200) -> str:
    """
    Summarize text (placeholder for future implementation)
    
    Args:
        text (str): Input text
        max_length (int): Maximum summary length
        
    Returns:
        str: Text summary
    """
    logger.warning("Text summarization not implemented yet")
    
    # Simple extractive summary (first few sentences)
    if nlp:
        doc = nlp(text)
        sentences = [sent.text for sent in doc.sents]
        
        # Take first few sentences up to max_length
        summary = ""
        for sentence in sentences:
            if len(summary + sentence) <= max_length:
                summary += sentence + " "
            else:
                break
                
        return summary.strip()
    
    return text[:max_length] + "..." if len(text) > max_length else text

def classify_document(text: str) -> Dict[str, Any]:
    """
    Classify document type/category (placeholder for future implementation)
    
    Args:
        text (str): Input text
        
    Returns:
        Dict: Document classification results
    """
    logger.warning("Document classification not implemented yet")
    return {
        "category": "general",
        "confidence": 0.5,
        "categories": {
            "general": 0.5,
            "technical": 0.3,
            "legal": 0.2
        }
    }
