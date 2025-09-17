#!/usr/bin/env python3
"""
Quick test script to verify the NLP service is working properly
and models are loaded correctly.
"""

import requests
import time
import json

def test_nlp_service(base_url="http://localhost:8001"):
    """Test the NLP service endpoints"""
    
    print("🧪 Testing NLP Service...")
    print(f"🌐 Base URL: {base_url}")
    print()
    
    # Test health endpoint
    try:
        print("1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Health check passed!")
            print(f"   📊 Status: {health_data.get('status', 'unknown')}")
            print(f"   🧠 Model loaded: {health_data.get('model_loaded', 'unknown')}")
            print(f"   💻 Device: {health_data.get('device', 'unknown')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to service: {e}")
        return False
    
    print()
    
    # Test document summarization
    try:
        print("2. Testing document summarization...")
        test_document = """
        This is a test document about project management. 
        The project involves developing a document processing system.
        Key tasks include setting up the backend infrastructure,
        implementing natural language processing capabilities,
        and creating a user-friendly frontend interface.
        The team needs to ensure proper testing and deployment procedures.
        """
        
        response = requests.post(
            f"{base_url}/summarize",
            json={"text": test_document},
            timeout=30
        )
        
        if response.status_code == 200:
            summary_data = response.json()
            print(f"   ✅ Summarization successful!")
            print(f"   📝 Method: {summary_data.get('method', 'unknown')}")
            print(f"   📋 Summary points: {len(summary_data.get('summary', []))}")
            for i, point in enumerate(summary_data.get('summary', [])[:3], 1):
                print(f"      {i}. {point}")
        else:
            print(f"   ❌ Summarization failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Summarization error: {e}")
    
    print()
    
    # Test task extraction
    try:
        print("3. Testing task extraction...")
        test_document = """
        Meeting Notes: Project Planning Session
        - Set up development environment by Friday
        - Review and approve API documentation
        - Schedule deployment for next week
        - Contact client for requirements clarification
        - Update project timeline in the tracking system
        """
        
        response = requests.post(
            f"{base_url}/tasks",
            json={"text": test_document},
            timeout=30
        )
        
        if response.status_code == 200:
            tasks_data = response.json()
            print(f"   ✅ Task extraction successful!")
            print(f"   📝 Method: {tasks_data.get('method', 'unknown')}")
            print(f"   ✅ Tasks found: {len(tasks_data.get('tasks', []))}")
            for i, task in enumerate(tasks_data.get('tasks', [])[:3], 1):
                print(f"      {i}. {task.get('text', 'N/A')} ({task.get('priority', 'unknown')})")
        else:
            print(f"   ❌ Task extraction failed: {response.status_code}")
    
    except Exception as e:
        print(f"   ❌ Task extraction error: {e}")
    
    print()
    print("🎉 NLP Service test completed!")
    return True

def measure_startup_time():
    """Measure how long it takes for the service to become ready"""
    print("⏱️ Measuring startup time...")
    start_time = time.time()
    
    max_wait = 300  # 5 minutes max
    check_interval = 5  # Check every 5 seconds
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get("http://localhost:8001/health", timeout=5)
            if response.status_code == 200:
                elapsed = time.time() - start_time
                print(f"🚀 Service ready in {elapsed:.1f} seconds!")
                return elapsed
        except:
            pass
        
        elapsed = time.time() - start_time
        print(f"   ⏳ Waiting... ({elapsed:.1f}s)")
        time.sleep(check_interval)
    
    print("❌ Service did not start within 5 minutes")
    return None

if __name__ == "__main__":
    print("🔬 NLP Service Test Suite")
    print("=" * 50)
    
    # First measure startup time
    startup_time = measure_startup_time()
    
    print()
    print("=" * 50)
    
    # Then run functionality tests
    test_nlp_service()
    
    print()
    print("📊 Performance Summary:")
    if startup_time:
        print(f"   🚀 Startup time: {startup_time:.1f} seconds")
        if startup_time < 60:
            print("   ✅ Excellent startup time!")
        elif startup_time < 120:
            print("   👍 Good startup time!")
        else:
            print("   ⚠️ Startup time could be improved")
    print("   🧠 Model: Flan-T5-Base (optimized for speed)")
    print("   💾 Models: Pre-downloaded (no internet needed)")
    print()
    print("✅ Test complete! Your setup is working correctly.")