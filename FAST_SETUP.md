# Fast Development Setup - One-Time Model Download

This guide ensures models download **only once** and containers start instantly afterward.

## The Problem You Had:
- **Every `docker-compose up`**: Downloaded 670MB PyTorch + 3GB model = 11+ minutes
- **Every container restart**: Re-downloaded models
- **Slow startup**: 5+ minutes each time

## The Solution - Download Once, Use Forever:

### Method 1: Docker Image with Pre-baked Models (Recommended)

Models are downloaded during Docker build and permanently stored in the image:

```bash
# Build once - models downloaded during build
docker-compose build nlp_service

# Run forever - starts in 30-60 seconds
docker-compose up
```

**After first build:**
- ✅ Container starts in 30-60 seconds (not 10+ minutes)
- ✅ No internet needed for model loading
- ✅ Models never re-download

### Method 2: Pre-download to Host Volume

Download models to your local machine once, then share with containers:

```bash
# Step 1: Download models once to local directory
python download_models_once.py ./models_cache

# Step 2: Update docker-compose to use local models
# (Add volume mapping: ./models_cache:/app/models)

# Step 3: Run containers - instant startup
docker-compose up
```

### Method 3: Development with Pre-downloaded Models

```bash
# Use development compose with optimized settings
docker-compose -f docker-compose.dev.yml up --build
```

## Build Time Comparison:

| Scenario | First Time | Subsequent Runs | Model Download |
|----------|------------|-----------------|----------------|
| **Before (Your Issue)** | 15+ min | 15+ min | Every time |
| **After (Method 1)** | 6-8 min | 30-60 sec | Once during build |
| **After (Method 2)** | 5 min setup | 30-60 sec | Once only |

## Model Size Optimization:

| Model | Size | Load Time | Quality | Status |
|-------|------|-----------|---------|--------|
| flan-t5-large | 3GB | 5+ min | Excellent | ❌ Too slow |
| **flan-t5-base** | 990MB | 30-60s | Very Good | ✅ **Current** |
| distilbert | 250MB | 10-20s | Good | 🔄 Future option |

## Quick Start Commands:

### 🚀 Instant Setup (Recommended):
```bash
# Build with models pre-downloaded (one time only)
docker-compose build nlp_service

# Run - starts instantly
docker-compose up
```

### 🔧 Development Setup:
```bash
# Fast development environment
docker-compose -f docker-compose.dev.yml up
```

### 🧹 Clean Start (if needed):
```bash
# Clean everything and rebuild with fresh models
docker-compose down -v
docker system prune -f
docker-compose build --no-cache nlp_service
docker-compose up
```

## How It Works:

### 1. **Multi-stage Docker Build:**
```dockerfile
# Stage 1: Install dependencies
# Stage 2: Download models (happens once)
# Stage 3: Copy models into final image
```

### 2. **Model Storage Locations:**
- **In Image**: `/app/models` (permanent, fast)
- **Host Volume**: `./models_cache` (shareable)
- **Docker Volume**: `nlp_models` (persistent)

### 3. **Smart Model Loading:**
```python
# App checks:
# 1. Are models in image? ✅ Load instantly
# 2. Are models in volume? ✅ Load from cache
# 3. Download needed? ⚠️ Download once
```

## Verification:

### Check if models are pre-installed:
```bash
# Should show pre-downloaded models
docker run --rm your-nlp-image ls -la /app/models
```

### Monitor startup time:
```bash
# Time the startup
time docker-compose up nlp_service
```

### Check container logs:
```bash
# Should show "Using pre-downloaded models"
docker-compose logs nlp_service
```

## Troubleshooting:

### If models still download:
```bash
# Rebuild with no cache
docker-compose build --no-cache nlp_service
```

### If startup is slow:
```bash
# Check if models exist in image
docker run --rm $(docker-compose images -q nlp_service) find /app/models -name "*.bin"
```

### Clear everything and start fresh:
```bash
docker-compose down -v
docker system prune -af
docker-compose build nlp_service
docker-compose up
```

## Expected Results:

✅ **First build**: 6-8 minutes (downloads models once)  
✅ **All subsequent runs**: 30-60 seconds startup  
✅ **No internet needed**: Models are in the image  
✅ **No re-downloads**: Ever  

Your containers will now start as fast as a simple web server! 🎉