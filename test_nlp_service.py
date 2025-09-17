#!/usr/bin/env python3
"""
Test script for the NLP service
Run this after docker-compose up to verify the service is working
"""

import requests
import json
import time

# Test document
test_document = """
KMRL Document Processing Test
This is a test document for the enhanced processing pipeline.

Action Items:
1. Please review this document
2. John should provide feedback by Friday
3. Update the report with new data

Additional Information:
This document contains various types of content including
action items, deadlines, and general information.
The system should be able to extract tasks and generate
meaningful summaries from this content.
"""

def test_nlp_service():
    base_url = "http://localhost:8001"  # NLP service port
    
    print("🧪 Testing NLP Service with Flan-T5-Large")
    print("=" * 50)
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed: {health_data}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test summarization
    print("\n2. Testing summarization...")
    try:
        response = requests.post(
            f"{base_url}/summarize",
            json={"text": test_document},
            timeout=120
        )
        if response.status_code == 200:
            summary_data = response.json()
            print(f"✅ Summary generated:")
            for i, point in enumerate(summary_data.get("summary", []), 1):
                print(f"   {i}. {point}")
        else:
            print(f"❌ Summarization failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Summarization error: {e}")
    
    # Test highlights
    print("\n3. Testing highlights...")
    try:
        response = requests.post(
            f"{base_url}/highlight",
            json={"text": test_document},
            timeout=120
        )
        if response.status_code == 200:
            highlight_data = response.json()
            print(f"✅ Highlights extracted:")
            for i, highlight in enumerate(highlight_data.get("highlights", []), 1):
                print(f"   {i}. {highlight}")
        else:
            print(f"❌ Highlighting failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Highlighting error: {e}")
    
    # Test task extraction
    print("\n4. Testing task extraction...")
    try:
        response = requests.post(
            f"{base_url}/tasks",
            json={"text": test_document},
            timeout=120
        )
        if response.status_code == 200:
            task_data = response.json()
            print(f"✅ Tasks extracted:")
            for i, task in enumerate(task_data.get("tasks", []), 1):
                print(f"   {i}. {task.get('text', 'N/A')} (Priority: {task.get('priority', 'N/A')})")
        else:
            print(f"❌ Task extraction failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Task extraction error: {e}")
    
    print("\n🎉 NLP Service testing completed!")
    return True

def wait_for_service():
    """Wait for the NLP service to be ready"""
    base_url = "http://localhost:8001"
    max_attempts = 30  # 5 minutes
    attempt = 0
    
    print("⏳ Waiting for NLP service to be ready...")
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                if health_data.get("model_loaded", False):
                    print("✅ NLP service is ready!")
                    return True
                else:
                    print(f"⏳ Model still loading... (attempt {attempt + 1}/{max_attempts})")
            else:
                print(f"⏳ Service not ready... (attempt {attempt + 1}/{max_attempts})")
        except Exception:
            print(f"⏳ Waiting for service... (attempt {attempt + 1}/{max_attempts})")
        
        time.sleep(10)
        attempt += 1
    
    print("❌ Timeout waiting for NLP service")
    return False

if __name__ == "__main__":
    if wait_for_service():
        test_nlp_service()
    else:
        print("❌ Could not connect to NLP service")
        print("Make sure to run: docker-compose up nlp_service") 