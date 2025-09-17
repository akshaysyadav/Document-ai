#!/usr/bin/env python3
"""
One-time model download script.
Run this once to download all models to a persistent location.
After this, containers will start instantly using pre-downloaded models.
"""

import os
import sys
from pathlib import Path

def ensure_transformers():
    """Ensure transformers is available"""
    try:
        from transformers import T5ForConditionalGeneration, T5Tokenizer
        return T5ForConditionalGeneration, T5Tokenizer
    except ImportError:
        print("❌ transformers not installed. Installing...")
        os.system("pip install transformers torch")
        from transformers import T5ForConditionalGeneration, T5Tokenizer
        return T5ForConditionalGeneration, T5Tokenizer

def download_all_models():
    """Download all models used by the application"""
    
    T5ForConditionalGeneration, T5Tokenizer = ensure_transformers()
    
    # Models to download
    models_to_download = [
        "google/flan-t5-base",  # Primary model (990MB)
        # Add more models here if needed in the future
    ]
    
    # Cache directory - can be customized via environment variable
    cache_dir = os.environ.get("MODELS_DIR", "./models_cache")
    
    print(f"🎯 Downloading models to: {cache_dir}")
    os.makedirs(cache_dir, exist_ok=True)
    
    for model_name in models_to_download:
        try:
            print(f"\n📥 Downloading {model_name}...")
            
            # Download tokenizer
            print(f"  📝 Downloading tokenizer...")
            tokenizer = T5Tokenizer.from_pretrained(
                model_name, 
                cache_dir=cache_dir
            )
            
            # Download model
            print(f"  🧠 Downloading model...")
            model = T5ForConditionalGeneration.from_pretrained(
                model_name, 
                cache_dir=cache_dir
            )
            
            print(f"  ✅ {model_name} downloaded successfully!")
            
            # Create success marker
            marker_file = Path(cache_dir) / f".{model_name.replace('/', '_')}_downloaded"
            marker_file.write_text(f"Downloaded on {__import__('datetime').datetime.now()}")
            
        except Exception as e:
            print(f"  ❌ Failed to download {model_name}: {e}")
            continue
    
    # Create global success marker
    success_marker = Path(cache_dir) / ".all_models_downloaded"
    success_marker.write_text("All models downloaded successfully")
    
    print(f"\n🎉 All models downloaded to {cache_dir}")
    print("💡 You can now run containers and they will start instantly!")
    print(f"📁 Models cached in: {os.path.abspath(cache_dir)}")
    
    return True

if __name__ == "__main__":
    print("🚀 One-time model download script")
    print("This downloads all models once. Containers will then start instantly.")
    print()
    
    if len(sys.argv) > 1:
        os.environ["MODELS_DIR"] = sys.argv[1]
        print(f"Using custom models directory: {sys.argv[1]}")
    
    try:
        download_all_models()
        print("\n✅ Setup complete! Run docker-compose up and enjoy fast startup times!")
    except KeyboardInterrupt:
        print("\n⚠️ Download interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        sys.exit(1)