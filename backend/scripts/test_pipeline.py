#!/usr/bin/env python3
"""
Test script for the document processing pipeline
"""
import os
import sys
import requests
import time
import logging
from pathlib import Path

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test API health check"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            logger.info("✅ API health check passed")
            return True
        else:
            logger.error(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ API health check failed: {e}")
        return False


def test_service_status():
    """Test service status endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/status")
        if response.status_code == 200:
            status = response.json()
            logger.info("📊 Service Status:")
            for service, health in status.items():
                status_icon = "✅" if health == "healthy" else "❌"
                logger.info(f"  {status_icon} {service}: {health}")
            return True
        else:
            logger.error(f"❌ Service status check failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Service status check failed: {e}")
        return False


def create_sample_pdf():
    """Create a sample PDF for testing"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Create a simple PDF with test content
        filename = "test_sample.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        
        # Add content
        c.drawString(100, 750, "KMRL Document Processing Test")
        c.drawString(100, 700, "This is a test document for the document processing pipeline.")
        c.drawString(100, 650, "")
        c.drawString(100, 600, "Action Items:")
        c.drawString(120, 570, "1. Please review this document")
        c.drawString(120, 540, "2. John should provide feedback by Friday")
        c.drawString(120, 510, "3. Update the report with new data")
        c.drawString(100, 470, "")
        c.drawString(100, 420, "Additional Information:")
        c.drawString(100, 390, "This document contains various types of content including")
        c.drawString(100, 360, "action items, deadlines, and general information.")
        c.drawString(100, 330, "The system should be able to extract tasks and generate")
        c.drawString(100, 300, "meaningful summaries from this content.")
        
        c.save()
        logger.info(f"✅ Created sample PDF: {filename}")
        return filename
    except ImportError:
        logger.warning("⚠️ reportlab not available, creating simple text file instead")
        # Create a simple text file as fallback
        filename = "test_sample.txt"
        with open(filename, "w") as f:
            f.write("KMRL Document Processing Test\n\n")
            f.write("This is a test document for the document processing pipeline.\n\n")
            f.write("Action Items:\n")
            f.write("1. Please review this document\n")
            f.write("2. John should provide feedback by Friday\n")
            f.write("3. Update the report with new data\n\n")
            f.write("Additional Information:\n")
            f.write("This document contains various types of content including\n")
            f.write("action items, deadlines, and general information.\n")
            f.write("The system should be able to extract tasks and generate\n")
            f.write("meaningful summaries from this content.\n")
        
        logger.info(f"✅ Created sample text file: {filename}")
        return filename


def test_document_upload(filename):
    """Test document upload"""
    try:
        logger.info(f"📤 Uploading document: {filename}")
        
        with open(filename, "rb") as f:
            files = {"file": (filename, f, "application/pdf" if filename.endswith(".pdf") else "text/plain")}
            data = {
                "title": "Test Document",
                "description": "A test document for pipeline testing",
                "tags": "test, pipeline, sample"
            }
            
            response = requests.post(f"{API_BASE_URL}/api/documents/", files=files, data=data)
            
            if response.status_code == 200:
                doc_data = response.json()
                doc_id = doc_data["id"]
                logger.info(f"✅ Document uploaded successfully: ID {doc_id}")
                return doc_id
            else:
                logger.error(f"❌ Document upload failed: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        logger.error(f"❌ Document upload failed: {e}")
        return None


def wait_for_processing(doc_id, max_wait_time=300):
    """Wait for document processing to complete"""
    logger.info(f"⏳ Waiting for document {doc_id} processing to complete...")
    
    start_time = time.time()
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(f"{API_BASE_URL}/api/documents/{doc_id}")
            if response.status_code == 200:
                doc_data = response.json()
                status = doc_data.get("status", "unknown")
                
                if status == "processed":
                    logger.info(f"✅ Document {doc_id} processing completed!")
                    return True
                elif status == "failed":
                    logger.error(f"❌ Document {doc_id} processing failed!")
                    return False
                else:
                    logger.info(f"🔄 Document {doc_id} status: {status}")
                    time.sleep(10)  # Wait 10 seconds before checking again
            else:
                logger.error(f"❌ Failed to check document status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error checking document status: {e}")
            time.sleep(10)
    
    logger.error(f"⏰ Timeout waiting for document {doc_id} processing")
    return False


def test_document_results(doc_id):
    """Test getting document results"""
    try:
        logger.info(f"📊 Getting results for document {doc_id}")
        
        response = requests.get(f"{API_BASE_URL}/api/documents/{doc_id}/results")
        if response.status_code == 200:
            results = response.json()
            
            logger.info("📋 Document Results:")
            logger.info(f"  📄 Title: {results['title']}")
            logger.info(f"  📝 Summary: {results['summary'][:100]}..." if results['summary'] else "  📝 Summary: None")
            logger.info(f"  📦 Chunks: {len(results['chunks'])}")
            logger.info(f"  ✅ Tasks: {len(results['tasks'])}")
            logger.info(f"  📊 Status: {results['status']}")
            
            # Show some tasks
            if results['tasks']:
                logger.info("🎯 Extracted Tasks:")
                for i, task in enumerate(results['tasks'][:3], 1):
                    logger.info(f"  {i}. {task['task_text']}")
                    if task.get('assignee'):
                        logger.info(f"     Assignee: {task['assignee']}")
                    if task.get('due_date'):
                        logger.info(f"     Due: {task['due_date']}")
            
            return True
        else:
            logger.error(f"❌ Failed to get document results: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error getting document results: {e}")
        return False


def test_document_report(doc_id):
    """Test getting document report"""
    try:
        logger.info(f"📈 Getting detailed report for document {doc_id}")
        
        response = requests.get(f"{API_BASE_URL}/api/documents/{doc_id}/report")
        if response.status_code == 200:
            report = response.json()
            
            logger.info("📊 Processing Report:")
            stats = report.get('statistics', {})
            logger.info(f"  📦 Total Chunks: {stats.get('total_chunks', 0)}")
            logger.info(f"  ✅ Processed Chunks: {stats.get('processed_chunks', 0)}")
            logger.info(f"  🎯 Total Tasks: {stats.get('total_tasks', 0)}")
            logger.info(f"  🔍 Has Embeddings: {stats.get('has_embeddings', False)}")
            
            return True
        else:
            logger.error(f"❌ Failed to get document report: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error getting document report: {e}")
        return False


def cleanup_test_files(filename):
    """Clean up test files"""
    try:
        if os.path.exists(filename):
            os.remove(filename)
            logger.info(f"🧹 Cleaned up test file: {filename}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to clean up {filename}: {e}")


def main():
    """Main test function"""
    logger.info("🧪 Starting KMRL Document Processing Pipeline Test")
    
    # Test API availability
    if not test_health_check():
        logger.error("💥 API is not available. Make sure the backend is running on http://localhost:8000")
        return
    
    test_service_status()
    
    # Create and upload test document
    filename = create_sample_pdf()
    doc_id = test_document_upload(filename)
    
    if doc_id:
        # Wait for processing
        if wait_for_processing(doc_id):
            # Test results
            test_document_results(doc_id)
            test_document_report(doc_id)
        
        # Cleanup
        cleanup_test_files(filename)
    
    logger.info("🏁 Pipeline test completed!")


if __name__ == "__main__":
    main()



