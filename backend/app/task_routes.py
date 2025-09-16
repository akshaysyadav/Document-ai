from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from .database import get_db
from .models import Task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.patch("/{task_id}")
async def update_task(
    task_id: str,
    updates: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Update a task with new status, assignee, or due date"""
    try:
        # Get task
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update fields
        if "status" in updates:
            task.status = updates["status"]
        if "assignee" in updates:
            task.assignee = updates["assignee"]
        if "due_date" in updates:
            from datetime import datetime
            if updates["due_date"]:
                task.due_date = datetime.fromisoformat(updates["due_date"])
            else:
                task.due_date = None
        if "priority" in updates:
            task.priority = updates["priority"]
        
        db.commit()
        
        return {
            "id": task.id,
            "task_text": task.task_text,
            "priority": task.priority,
            "status": task.status,
            "assignee": task.assignee,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "chunk_id": task.chunk_id,
            "document_id": task.document_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
