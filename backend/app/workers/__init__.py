"""
Workers package for KMRL Document AI Backend
"""
import os
import sys
from rq import Worker, Connection
from app.database import redis_client, ocr_queue, nlp_queue, post_process_queue

def run_worker():
    """
    Start RQ worker to process background jobs
    """
    # Get queue names from environment or use defaults
    queue_names = os.getenv('RQ_QUEUES', 'ocr,nlp,post_process').split(',')
    
    with Connection(redis_client):
        worker = Worker(queue_names)
        print(f"🎯 Worker listening on queues: {queue_names}")
        worker.work(with_scheduler=True)

def enqueue_document_processing(document_id: int):
    """
    Enqueue document processing job
    """
    from .document_processor import process_document
    
    # Enqueue the main document processing job with None for db session (queue worker will create new session)
    job = ocr_queue.enqueue(process_document, document_id, None)
    print(f"📋 Enqueued document processing job {job.id} for document {document_id}")
    return job

if __name__ == "__main__":
    run_worker()
