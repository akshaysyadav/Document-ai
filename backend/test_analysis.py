#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def test_document_analysis():
    base_url = "http://localhost:8000"
    
    # Test document data
    doc_data = {
        "title": "Test Document for Analysis",
        "description": "A sample document to test the AI analysis feature",
        "content": "This is a test document for the KMRL Document Intelligence system. We need to complete the following tasks: 1. Review the safety protocols, 2. Update the passenger information system, 3. Schedule maintenance for next week, 4. Prepare the monthly report by Friday. The system should automatically extract these action items and provide a summary.",
        "tags": '["test", "analysis", "sample"]'
    }
    
    print("Creating test document...")
    
    # Create document using form data
    response = requests.post(f"{base_url}/api/documents/", data=doc_data)
    if response.status_code == 200:
        document = response.json()
        doc_id = document["id"]
        print(f"✅ Document created successfully with ID: {doc_id}")
        print(f"Title: {document['title']}")
        
        # Test analysis
        print(f"\nTesting analysis for document {doc_id}...")
        analysis_response = requests.post(f"{base_url}/api/documents/{doc_id}/analyze")
        
        if analysis_response.status_code == 200:
            analysis = analysis_response.json()
            print("✅ Analysis completed successfully!")
            print(f"Summary: {analysis['summary']}")
            print(f"Tasks: {analysis['tasks']}")
        else:
            print(f"❌ Analysis failed: {analysis_response.status_code}")
            print(f"Error: {analysis_response.text}")
    else:
        print(f"❌ Document creation failed: {response.status_code}")
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_document_analysis()