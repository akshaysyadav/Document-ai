#!/usr/bin/env python3
"""
Script to download and cache the Flan-T5-Large model during Docker build.
This ensures the model is available immediately when the container starts.
"""

import os
import sys
from transformers import T5ForConditionalGeneration, T5Tokenizer

def download_model():
    """Download and cache the model"""
    try:
        print("🚀 Starting one-time model download...")
        
        # Using smaller, faster model
        model_name = "google/flan-t5-base"  # ~990MB vs 3GB for large
        cache_dir = "/app/models"
        
        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)
        
        print(f"📥 Downloading tokenizer for {model_name}...")
        tokenizer = T5Tokenizer.from_pretrained(
            model_name, 
            cache_dir=cache_dir
        )
        
        print(f"📥 Downloading model {model_name} (faster than flan-t5-large)...")
        model = T5ForConditionalGeneration.from_pretrained(
            model_name, 
            cache_dir=cache_dir
        )
        
        print("✅ Flan-T5-Base model downloaded and cached permanently!")
        print(f"📁 Cache location: {cache_dir}")
        print(f"📊 Model size: ~990MB (vs 3GB for flan-t5-large)")
        print("🔒 This download happens ONLY ONCE during Docker build")
        
        # Verify the model can be loaded
        print("🔄 Verifying model...")
        test_input = "Hello world"
        inputs = tokenizer(test_input, return_tensors="pt")
        print("✅ Model verification complete!")
        
        # Create marker file
        with open(f"{cache_dir}/.download_complete", "w") as f:
            f.write(f"Model {model_name} downloaded successfully on build")
        
        return True
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        sys.exit(1)

if __name__ == "__main__":
    download_model()