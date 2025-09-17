import logging
import os
from typing import Dict, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model and tokenizer
model = None
tokenizer = None

class TextRequest(BaseModel):
    text: str

class SummaryResponse(BaseModel):
    summary: List[str]
    method: str = "flan-t5-base"

class HighlightResponse(BaseModel):
    highlights: List[str]
    method: str = "flan-t5-base"

class TasksResponse(BaseModel):
    tasks: List[Dict[str, str]]
    method: str = "flan-t5-base"

async def load_model():
    """Load the Flan-T5-Base model and tokenizer (pre-downloaded during build)"""
    global model, tokenizer
    
    try:
        logger.info("Loading pre-downloaded Flan-T5-Base model...")
        
        # Check if models were pre-downloaded during build
        models_dir = "/app/models"
        if os.path.exists(f"{models_dir}/.download_complete"):
            logger.info("✅ Using pre-downloaded models from Docker image")
        elif os.path.exists(f"{models_dir}/.models_ready"):
            logger.info("✅ Using models from persistent volume")
        else:
            logger.warning("⚠️ Models not found, downloading now (this should only happen once)")
        
        # Using smaller, faster model instead of flan-t5-large
        model_name = "google/flan-t5-base"  # ~990MB vs 3GB for large
        
        # Load tokenizer and model from cache (should be instant if pre-downloaded)
        tokenizer = T5Tokenizer.from_pretrained(
            model_name,
            cache_dir=models_dir
        )
        model = T5ForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=torch.float32,  # CPU optimized
            device_map=None,
            cache_dir=models_dir
        )
        
        # Always use CPU for better compatibility and faster startup
        model = model.to('cpu')
        
        logger.info(f"✅ Flan-T5-Base model loaded successfully on CPU")
        logger.info("🚀 Ready to process documents!")
        
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        raise e

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await load_model()
    yield
    # Shutdown
    logger.info("Shutting down NLP service...")

# Create FastAPI app
app = FastAPI(
    title="KMRL NLP Service",
    description="Optimized NLP service using Flan-T5-Base for fast document processing",
    version="1.0.0",
    lifespan=lifespan
)

def generate_response(prompt: str, max_length: int = 512) -> str:
    """Generate response using Flan-T5-Large"""
    try:
        # Tokenize input
        inputs = tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)
        
        # Move inputs to same device as model
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=max_length,
                num_beams=4,
                temperature=0.7,
                do_sample=True,
                early_stopping=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.strip()
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")

def parse_bullet_points(text: str) -> List[str]:
    """Parse text into bullet points"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # If already in bullet format, return as is
    if any(line.startswith(('•', '-', '*', '1.', '2.', '3.')) for line in lines):
        return [line.lstrip('•-*0123456789. ').strip() for line in lines if line.strip()]
    
    # If single paragraph, split by sentences and take first 5
    if len(lines) == 1:
        sentences = [s.strip() for s in lines[0].split('.') if s.strip()]
        return sentences[:5]
    
    # Return lines as bullet points
    return lines[:5]

def parse_tasks(text: str) -> List[Dict[str, str]]:
    """Parse text into structured tasks"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    tasks = []
    
    for line in lines:
        # Clean up the line
        task_text = line.lstrip('•-*0123456789. ').strip()
        
        if len(task_text) > 10:  # Only meaningful tasks
            # Determine priority based on keywords
            priority = "medium"
            if any(word in task_text.lower() for word in ['urgent', 'critical', 'immediate', 'asap']):
                priority = "high"
            elif any(word in task_text.lower() for word in ['optional', 'nice to have', 'when possible']):
                priority = "low"
            
            tasks.append({
                "text": task_text,
                "priority": priority,
                "status": "open"
            })
    
    return tasks

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "device": str(next(model.parameters()).device) if model else "unknown"
    }

@app.post("/summarize", response_model=SummaryResponse)
async def summarize_document(request: TextRequest):
    """Summarize document into concise bullet points"""
    if not model or not tokenizer:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Truncate text if too long
        text = request.text[:4000] if len(request.text) > 4000 else request.text
        
        prompt = f"Summarize this document in 5 concise bullet points:\n\n{text}"
        
        logger.info(f"Generating summary for {len(text)} characters")
        response = generate_response(prompt, max_length=300)
        
        # Parse into bullet points
        bullet_points = parse_bullet_points(response)
        
        # Ensure we have at least one point
        if not bullet_points:
            bullet_points = ["Document summary could not be generated."]
        
        logger.info(f"Generated {len(bullet_points)} summary points")
        
        return SummaryResponse(summary=bullet_points)
        
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

@app.post("/highlight", response_model=HighlightResponse)
async def highlight_document(request: TextRequest):
    """Extract key ideas and important sections"""
    if not model or not tokenizer:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Truncate text if too long
        text = request.text[:4000] if len(request.text) > 4000 else request.text
        
        prompt = f"List the most important sections or ideas in this document:\n\n{text}"
        
        logger.info(f"Extracting highlights for {len(text)} characters")
        response = generate_response(prompt, max_length=400)
        
        # Parse into highlights
        highlights = parse_bullet_points(response)
        
        # Ensure we have at least one highlight
        if not highlights:
            highlights = ["No key highlights could be identified."]
        
        logger.info(f"Generated {len(highlights)} highlights")
        
        return HighlightResponse(highlights=highlights)
        
    except Exception as e:
        logger.error(f"Highlighting failed: {e}")
        raise HTTPException(status_code=500, detail=f"Highlighting failed: {str(e)}")

@app.post("/tasks", response_model=TasksResponse)
async def extract_tasks(request: TextRequest):
    """Extract actionable tasks from document"""
    if not model or not tokenizer:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Truncate text if too long
        text = request.text[:4000] if len(request.text) > 4000 else request.text
        
        prompt = f"Extract all action items or tasks from this document. A task means something that requires someone to do an action:\n\n{text}"
        
        logger.info(f"Extracting tasks for {len(text)} characters")
        response = generate_response(prompt, max_length=400)
        
        # Parse into structured tasks
        tasks = parse_tasks(response)
        
        # If no meaningful tasks found
        if not tasks:
            tasks = [{
                "text": "No actionable tasks found in this document.",
                "priority": "low",
                "status": "info"
            }]
        
        logger.info(f"Generated {len(tasks)} tasks")
        
        return TasksResponse(tasks=tasks)
        
    except Exception as e:
        logger.error(f"Task extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Task extraction failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "KMRL NLP Service",
        "model": "google/flan-t5-base",
        "endpoints": {
            "summarize": "POST /summarize - Generate document summary",
            "highlight": "POST /highlight - Extract key highlights", 
            "tasks": "POST /tasks - Extract actionable tasks",
            "health": "GET /health - Health check"
        },
        "status": "ready" if model else "loading"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 