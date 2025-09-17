#!/usr/bin/env python3
"""
Worker runner script for KMRL Document AI Backend
"""
import os
import sys
import logging

# Add the app directory to Python path
sys.path.append(os.path.dirname(__file__))

from app.workers import run_worker

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    print("🚀 Starting KMRL Document AI Worker...")
    print("📋 Processing queues: ocr, nlp, post_process")
    print("⏳ Worker is running... Press Ctrl+C to stop")
    
    try:
        run_worker()
    except KeyboardInterrupt:
        print("\n🛑 Worker stopped by user")
    except Exception as e:
        print(f"💥 Worker failed: {e}")
        sys.exit(1)


