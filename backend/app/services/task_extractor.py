"""
Task extraction service for identifying actionable tasks from text.
Supports rule-based extraction and LLM-based extraction.
"""
import logging
import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import openai
from ..settings import settings
from ..models import TaskPriority

logger = logging.getLogger(__name__)


class TaskExtractorService:
    def __init__(self):
        self.use_openai = settings.USE_OPENAI
        self.openai_api_key = settings.OPENAI_API_KEY
        self.task_extractor_model = settings.TASK_EXTRACTOR_MODEL
        
        # Initialize OpenAI if configured
        if self.use_openai and self.openai_api_key:
            openai.api_key = self.openai_api_key
            logger.info("OpenAI task extraction service initialized")
    
    def extract_tasks(self, text: str, doc_id: int, chunk_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Extract actionable tasks from text
        
        Args:
            text: Input text to analyze
            doc_id: Document ID for task association
            chunk_id: Optional chunk ID for task source tracking
            
        Returns:
            List of task dictionaries
        """
        try:
            # Always run rule-based extraction first
            rule_based_tasks = self._extract_tasks_rule_based(text, doc_id, chunk_id)
            
            # If LLM is configured, also try LLM extraction
            llm_tasks = []
            if self.use_openai and self.openai_api_key:
                try:
                    llm_tasks = self._extract_tasks_with_llm(text, doc_id, chunk_id)
                except Exception as e:
                    logger.warning(f"LLM task extraction failed: {e}")
            
            # Combine and deduplicate tasks
            all_tasks = rule_based_tasks + llm_tasks
            deduplicated_tasks = self._deduplicate_tasks(all_tasks)
            
            logger.info(f"Extracted {len(deduplicated_tasks)} tasks from text")
            return deduplicated_tasks
            
        except Exception as e:
            logger.error(f"Task extraction failed: {e}")
            return []
    
    def _extract_tasks_rule_based(self, text: str, doc_id: int, chunk_id: Optional[str]) -> List[Dict[str, Any]]:
        """Extract tasks using rule-based patterns"""
        tasks = []
        
        # Pattern 1: Action items with explicit markers
        action_patterns = [
            r'Action:\s*(.+?)(?:\n|$)',
            r'Action Item:\s*(.+?)(?:\n|$)',
            r'To Do:\s*(.+?)(?:\n|$)',
            r'TODO:\s*(.+?)(?:\n|$)',
            r'Task:\s*(.+?)(?:\n|$)',
        ]
        
        for pattern in action_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                task_text = match.group(1).strip()
                if task_text:
                    tasks.append(self._create_task_dict(
                        task_text=task_text,
                        doc_id=doc_id,
                        chunk_id=chunk_id,
                        extracted_by="rule-based",
                        priority=self._determine_priority(task_text),
                        assignee=self._extract_assignee(task_text),
                        due_date=self._extract_due_date(task_text)
                    ))
        
        # Pattern 2: Requests and polite commands
        request_patterns = [
            r'Please\s+(.+?)(?:\.|$|\n)',
            r'Kindly\s+(.+?)(?:\.|$|\n)',
            r'Could you\s+(.+?)(?:\?|$|\n)',
            r'Can you\s+(.+?)(?:\?|$|\n)',
            r'Would you\s+(.+?)(?:\?|$|\n)',
        ]
        
        for pattern in request_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                task_text = match.group(1).strip()
                if task_text and len(task_text) > 10:  # Filter out very short matches
                    tasks.append(self._create_task_dict(
                        task_text=f"Please {task_text}",
                        doc_id=doc_id,
                        chunk_id=chunk_id,
                        extracted_by="rule-based",
                        priority=self._determine_priority(task_text),
                        assignee=self._extract_assignee(task_text),
                        due_date=self._extract_due_date(task_text)
                    ))
        
        # Pattern 3: Bullet points with action verbs
        bullet_patterns = [
            r'[-*•]\s*(.+?)(?:\n|$)',
            r'\d+\.\s*(.+?)(?:\n|$)',
        ]
        
        action_verbs = [
            'create', 'develop', 'implement', 'build', 'design', 'write', 'review',
            'analyze', 'update', 'fix', 'resolve', 'complete', 'finish', 'submit',
            'send', 'prepare', 'organize', 'schedule', 'arrange', 'coordinate'
        ]
        
        for pattern in bullet_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                task_text = match.group(1).strip()
                # Check if it starts with an action verb
                first_word = task_text.lower().split()[0] if task_text.split() else ""
                if first_word in action_verbs and len(task_text) > 5:
                    tasks.append(self._create_task_dict(
                        task_text=task_text,
                        doc_id=doc_id,
                        chunk_id=chunk_id,
                        extracted_by="rule-based",
                        priority=self._determine_priority(task_text),
                        assignee=self._extract_assignee(task_text),
                        due_date=self._extract_due_date(task_text)
                    ))
        
        # Pattern 4: Due date mentions
        due_patterns = [
            r'Due by\s+(.+?)(?:\n|$)',
            r'Deadline:\s*(.+?)(?:\n|$)',
            r'Due date:\s*(.+?)(?:\n|$)',
            r'By\s+(.+?)(?:\n|$)',
        ]
        
        for pattern in due_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                task_text = match.group(1).strip()
                if task_text:
                    tasks.append(self._create_task_dict(
                        task_text=task_text,
                        doc_id=doc_id,
                        chunk_id=chunk_id,
                        extracted_by="rule-based",
                        priority=TaskPriority.HIGH,  # Due dates usually indicate high priority
                        assignee=self._extract_assignee(task_text),
                        due_date=self._extract_due_date(task_text)
                    ))
        
        return tasks
    
    def _extract_tasks_with_llm(self, text: str, doc_id: int, chunk_id: Optional[str]) -> List[Dict[str, Any]]:
        """Extract tasks using LLM"""
        try:
            prompt = f"""
You are a precise task extractor. Analyze the following text and identify actionable tasks. 
Return a JSON array of tasks. Each task should have the following structure:
{{
    "task_text": "The actionable task description",
    "assignee": "Person responsible (if mentioned, otherwise null)",
    "due_date": "ISO date string or null if no date mentioned",
    "priority": "low/medium/high or null if unclear",
    "confidence": "0-1 confidence score"
}}

Rules:
1. Only extract clear, actionable tasks
2. If no tasks are found, return an empty array
3. Be conservative - only include items that are clearly tasks
4. Extract assignees from phrases like "John should", "Team X will", etc.
5. Extract dates from phrases like "by Friday", "due 2024-01-15", etc.
6. Determine priority based on urgency words and due dates

Text to analyze:
{text}
"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a precise task extractor that returns valid JSON arrays."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                tasks_data = json.loads(result)
                if not isinstance(tasks_data, list):
                    tasks_data = []
                
                tasks = []
                for task_data in tasks_data:
                    if isinstance(task_data, dict) and task_data.get('task_text'):
                        tasks.append(self._create_task_dict(
                            task_text=task_data['task_text'],
                            doc_id=doc_id,
                            chunk_id=chunk_id,
                            extracted_by="llm",
                            priority=self._parse_priority(task_data.get('priority')),
                            assignee=task_data.get('assignee'),
                            due_date=self._parse_due_date(task_data.get('due_date')),
                            metadata={'confidence': task_data.get('confidence', 0.5)}
                        ))
                
                return tasks
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM JSON response: {e}")
                return []
                
        except Exception as e:
            logger.error(f"LLM task extraction failed: {e}")
            return []
    
    def _create_task_dict(self, task_text: str, doc_id: int, chunk_id: Optional[str], 
                         extracted_by: str, priority: TaskPriority = TaskPriority.MEDIUM,
                         assignee: Optional[str] = None, due_date: Optional[datetime] = None,
                         metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a standardized task dictionary"""
        return {
            'task_text': task_text.strip(),
            'doc_id': doc_id,
            'source_chunk_id': chunk_id,
            'assignee': assignee,
            'due_date': due_date,
            'priority': priority,
            'status': 'open',
            'extracted_by': extracted_by,
            'metadata': metadata or {}
        }
    
    def _determine_priority(self, text: str) -> TaskPriority:
        """Determine task priority based on text content"""
        text_lower = text.lower()
        
        high_priority_indicators = [
            'urgent', 'asap', 'immediately', 'critical', 'emergency',
            'deadline', 'due today', 'due tomorrow', 'high priority'
        ]
        
        low_priority_indicators = [
            'when possible', 'eventually', 'low priority', 'nice to have',
            'optional', 'if time permits'
        ]
        
        for indicator in high_priority_indicators:
            if indicator in text_lower:
                return TaskPriority.HIGH
        
        for indicator in low_priority_indicators:
            if indicator in text_lower:
                return TaskPriority.LOW
        
        return TaskPriority.MEDIUM
    
    def _extract_assignee(self, text: str) -> Optional[str]:
        """Extract assignee from task text"""
        # Look for patterns like "John should", "Team X will", etc.
        patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:should|will|must|needs to)',
            r'(?:assign to|give to|delegate to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:is responsible|will handle)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_due_date(self, text: str) -> Optional[datetime]:
        """Extract due date from task text"""
        # Look for various date patterns
        patterns = [
            r'by\s+([A-Za-z]+\s+\d{1,2})',  # "by January 15"
            r'due\s+([A-Za-z]+\s+\d{1,2})',  # "due January 15"
            r'(\d{4}-\d{2}-\d{2})',  # "2024-01-15"
            r'(\d{1,2}/\d{1,2}/\d{4})',  # "1/15/2024"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                try:
                    # Try different date parsing approaches
                    if '/' in date_str:
                        return datetime.strptime(date_str, '%m/%d/%Y')
                    elif '-' in date_str:
                        return datetime.strptime(date_str, '%Y-%m-%d')
                    else:
                        # Handle "January 15" format
                        current_year = datetime.now().year
                        return datetime.strptime(f"{date_str} {current_year}", '%B %d %Y')
                except ValueError:
                    continue
        
        return None
    
    def _parse_priority(self, priority_str: Optional[str]) -> TaskPriority:
        """Parse priority string from LLM response"""
        if not priority_str:
            return TaskPriority.MEDIUM
        
        priority_lower = priority_str.lower()
        if priority_lower in ['high', 'urgent', 'critical']:
            return TaskPriority.HIGH
        elif priority_lower in ['low', 'low priority']:
            return TaskPriority.LOW
        else:
            return TaskPriority.MEDIUM
    
    def _parse_due_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse due date from LLM response"""
        if not date_str:
            return None
        
        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            try:
                # Try other common formats
                return datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                return None
    
    def _deduplicate_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate tasks based on normalized text"""
        seen = set()
        unique_tasks = []
        
        for task in tasks:
            # Normalize task text for comparison
            normalized = re.sub(r'[^\w\s]', '', task['task_text'].lower()).strip()
            normalized = re.sub(r'\s+', ' ', normalized)
            
            if normalized not in seen and len(normalized) > 5:
                seen.add(normalized)
                unique_tasks.append(task)
        
        return unique_tasks


# Global instance
task_extractor_service = TaskExtractorService()

