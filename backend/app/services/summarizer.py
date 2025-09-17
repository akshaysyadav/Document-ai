"""
Summarization service for generating text summaries using various models.
Supports HuggingFace transformers and OpenAI with fallbacks.
"""
import logging
from typing import List, Optional
import openai
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from ..settings import settings

logger = logging.getLogger(__name__)


class SummarizerService:
    def __init__(self):
        self.model_name = settings.SUMMARIZER_MODEL_NAME
        self.use_openai = settings.USE_OPENAI
        self.openai_api_key = settings.OPENAI_API_KEY
        self.summarizer_pipeline = None
        self.tokenizer = None
        self.model = None
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize summarization models"""
        try:
            if self.use_openai and self.openai_api_key:
                openai.api_key = self.openai_api_key
                logger.info("OpenAI summarization service initialized")
            else:
                # Try to load HuggingFace pipeline
                try:
                    self.summarizer_pipeline = pipeline(
                        "summarization",
                        model=self.model_name,
                        device=0 if torch.cuda.is_available() else -1
                    )
                    logger.info(f"HuggingFace summarization model loaded: {self.model_name}")
                except Exception as e:
                    logger.warning(f"Failed to load {self.model_name}, trying fallback: {e}")
                    # Try fallback model
                    try:
                        fallback_model = "google/flan-t5-small"
                        self.summarizer_pipeline = pipeline(
                            "summarization",
                            model=fallback_model,
                            device=0 if torch.cuda.is_available() else -1
                        )
                        logger.info(f"Fallback summarization model loaded: {fallback_model}")
                    except Exception as fallback_error:
                        logger.error(f"Failed to load fallback model: {fallback_error}")
                        # Load components separately for more control
                        self._load_model_components()
                        
        except Exception as e:
            logger.error(f"Failed to initialize summarization models: {e}")
    
    def _load_model_components(self):
        """Load tokenizer and model separately for more control"""
        try:
            fallback_model = "google/flan-t5-small"
            self.tokenizer = AutoTokenizer.from_pretrained(fallback_model)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(fallback_model)
            
            if torch.cuda.is_available():
                self.model = self.model.cuda()
                
            logger.info(f"Model components loaded separately: {fallback_model}")
        except Exception as e:
            logger.error(f"Failed to load model components: {e}")
    
    def summarize_text(self, text: str, max_length: int = 200, min_length: int = 50) -> str:
        """
        Summarize a single text
        
        Args:
            text: Input text to summarize
            max_length: Maximum length of summary
            min_length: Minimum length of summary
            
        Returns:
            Summarized text
        """
        try:
            if not text or len(text.strip()) < min_length:
                return text  # Return original if too short
            
            if self.use_openai and self.openai_api_key:
                return self._summarize_with_openai(text, max_length)
            else:
                return self._summarize_with_huggingface(text, max_length, min_length)
                
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            # Fallback to extractive summary
            return self._extractive_summary(text, max_length)
    
    def summarize_texts_batch(self, texts: List[str], max_length: int = 200, min_length: int = 50) -> List[str]:
        """
        Summarize multiple texts
        
        Args:
            texts: List of texts to summarize
            max_length: Maximum length of each summary
            min_length: Minimum length of each summary
            
        Returns:
            List of summarized texts
        """
        summaries = []
        for text in texts:
            summary = self.summarize_text(text, max_length, min_length)
            summaries.append(summary)
        return summaries
    
    def _summarize_with_openai(self, text: str, max_length: int) -> str:
        """Summarize using OpenAI API"""
        try:
            # Truncate text if too long (OpenAI has token limits)
            if len(text) > 4000:  # Rough approximation
                text = text[:4000] + "..."
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise summaries."},
                    {"role": "user", "content": f"Please summarize the following text in {max_length} words or less:\n\n{text}"}
                ],
                max_tokens=max_length * 2,  # Allow some buffer
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI summarization failed: {e}")
            raise
    
    def _summarize_with_huggingface(self, text: str, max_length: int, min_length: int) -> str:
        """Summarize using HuggingFace transformers"""
        try:
            if self.summarizer_pipeline:
                # Truncate text if too long for the model
                if len(text) > 1024:  # Most models have input limits
                    text = text[:1024] + "..."
                
                result = self.summarizer_pipeline(
                    text,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False,
                    truncation=True
                )
                
                return result[0]['summary_text']
            elif self.model and self.tokenizer:
                return self._summarize_with_model_components(text, max_length, min_length)
            else:
                raise Exception("No summarization model available")
                
        except Exception as e:
            logger.error(f"HuggingFace summarization failed: {e}")
            raise
    
    def _summarize_with_model_components(self, text: str, max_length: int, min_length: int) -> str:
        """Summarize using separately loaded model components"""
        try:
            # Tokenize input
            inputs = self.tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=512, truncation=True)
            
            # Generate summary
            with torch.no_grad():
                summary_ids = self.model.generate(
                    inputs,
                    max_length=max_length,
                    min_length=min_length,
                    length_penalty=2.0,
                    num_beams=4,
                    early_stopping=True
                )
            
            # Decode summary
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            return summary
            
        except Exception as e:
            logger.error(f"Model components summarization failed: {e}")
            raise
    
    def _extractive_summary(self, text: str, max_length: int) -> str:
        """Fallback extractive summary (simple sentence selection)"""
        try:
            sentences = text.split('. ')
            
            # Simple heuristic: take first few sentences up to max_length
            summary = ""
            for sentence in sentences:
                if len(summary + sentence + '. ') <= max_length:
                    summary += sentence + '. '
                else:
                    break
            
            return summary.strip()
        except Exception as e:
            logger.error(f"Extractive summary failed: {e}")
            return text[:max_length] + "..." if len(text) > max_length else text
    
    def hierarchical_summarize(self, texts: List[str], max_chunk_summary: int = 150, max_final_summary: int = 300) -> str:
        """
        Perform hierarchical summarization:
        1. Summarize each text chunk
        2. Combine chunk summaries and summarize again
        
        Args:
            texts: List of text chunks
            max_chunk_summary: Max length for individual chunk summaries
            max_final_summary: Max length for final summary
            
        Returns:
            Hierarchical summary
        """
        try:
            # Step 1: Summarize each chunk
            chunk_summaries = []
            for text in texts:
                chunk_summary = self.summarize_text(text, max_chunk_summary)
                chunk_summaries.append(chunk_summary)
            
            # Step 2: Combine chunk summaries and summarize again
            combined_summaries = " ".join(chunk_summaries)
            final_summary = self.summarize_text(combined_summaries, max_final_summary)
            
            return final_summary
            
        except Exception as e:
            logger.error(f"Hierarchical summarization failed: {e}")
            # Fallback to simple concatenation
            return " ".join(texts[:5])[:max_final_summary] + "..."


# Global instance
summarizer_service = SummarizerService()

