import logging
import httpx
from typing import Dict, List, Any, Optional
import asyncio
import os
from .settings import settings

logger = logging.getLogger(__name__)

class NLPServiceClient:
    """Client for communicating with the NLP service"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("NLP_SERVICE_URL", "http://localhost:8001")
        self.timeout = 120.0  # 2 minutes for model inference
    
    async def _make_request(self, endpoint: str, text: str) -> Dict[str, Any]:
        """Make request to NLP service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/{endpoint}",
                    json={"text": text},
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            logger.error(f"NLP service timeout for {endpoint}")
            raise Exception(f"NLP service timeout for {endpoint}")
        except httpx.RequestError as e:
            logger.error(f"NLP service request error: {e}")
            raise Exception(f"NLP service unavailable: {str(e)}")
        except httpx.HTTPStatusError as e:
            logger.error(f"NLP service HTTP error: {e.response.status_code}")
            raise Exception(f"NLP service error: {e.response.status_code}")
    
    def _make_request_sync(self, endpoint: str, text: str) -> Dict[str, Any]:
        """Synchronous wrapper for async request"""
        try:
            return asyncio.run(self._make_request(endpoint, text))
        except Exception as e:
            logger.error(f"Failed to call NLP service {endpoint}: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if NLP service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200 and response.json().get("model_loaded", False)
        except Exception:
            return False
    
    def generate_summary(self, text: str) -> str:
        """Generate summary using Flan-T5-Large"""
        try:
            logger.info("Calling NLP service for summary generation")
            response = self._make_request_sync("summarize", text)
            
            summary_points = response.get("summary", [])
            if summary_points:
                # Join bullet points into a coherent summary
                summary = "\n".join(f"• {point}" for point in summary_points)
                logger.info(f"Generated summary with {len(summary_points)} points")
                return summary
            else:
                return "Summary could not be generated."
                
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            # Fallback to simple extractive summary
            return self._fallback_summary(text)
    
    def extract_highlights(self, text: str) -> List[str]:
        """Extract key highlights using Flan-T5-Large"""
        try:
            logger.info("Calling NLP service for highlight extraction")
            response = self._make_request_sync("highlight", text)
            
            highlights = response.get("highlights", [])
            logger.info(f"Extracted {len(highlights)} highlights")
            return highlights
            
        except Exception as e:
            logger.error(f"Highlight extraction failed: {e}")
            return []
    
    def extract_tasks(self, text: str) -> List[Dict[str, str]]:
        """Extract tasks using Flan-T5-Large"""
        try:
            logger.info("Calling NLP service for task extraction")
            response = self._make_request_sync("tasks", text)
            
            tasks = response.get("tasks", [])
            logger.info(f"Extracted {len(tasks)} tasks")
            return tasks
            
        except Exception as e:
            logger.error(f"Task extraction failed: {e}")
            # Fallback to rule-based extraction
            return self._fallback_tasks(text)
    
    def generate_ai_summary_and_tasks(self, text: str) -> Dict[str, Any]:
        """Generate both summary and tasks using Flan-T5-Large"""
        try:
            logger.info("Generating AI summary and tasks using NLP service")
            
            # Make both requests
            summary = self.generate_summary(text)
            tasks = self.extract_tasks(text)
            
            return {
                "summary": summary,
                "tasks": tasks,
                "method": "flan-t5-large"
            }
            
        except Exception as e:
            logger.error(f"AI processing failed: {e}")
            # Fallback to simple methods
            return {
                "summary": self._fallback_summary(text),
                "tasks": self._fallback_tasks(text),
                "method": "fallback"
            }
    
    def _fallback_summary(self, text: str) -> str:
        """Simple fallback summary generation"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return "Document processed successfully."
        
        # Take first line as title and create basic summary
        title = lines[0]
        if len(title) > 100:
            title = title[:100] + "..."
        
        summary_parts = [f"Document: {title}"]
        
        # Look for key information
        key_lines = []
        for line in lines[1:5]:
            if any(keyword in line.lower() for keyword in ['email', 'phone', 'university', 'company', 'experience', 'skills']):
                key_lines.append(line[:80] + "..." if len(line) > 80 else line)
        
        if key_lines:
            summary_parts.append(f"Key details: {', '.join(key_lines[:2])}")
        
        return ". ".join(summary_parts) + "."
    
    def _fallback_tasks(self, text: str) -> List[Dict[str, str]]:
        """Simple fallback task extraction"""
        tasks = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for action-oriented sentences
            if (len(line) > 15 and 
                any(action in line.lower() for action in ['review', 'update', 'provide', 'complete', 'send', 'call', 'email', 'schedule'])):
                
                tasks.append({
                    "text": line,
                    "priority": "medium",
                    "status": "open"
                })
        
        # If no tasks found, return default message
        if not tasks:
            tasks = [{
                "text": "No actionable tasks found in this document.",
                "priority": "low",
                "status": "open"
            }]
        
        return tasks

# Create global client instance
nlp_client = NLPServiceClient() 