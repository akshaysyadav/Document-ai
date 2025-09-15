#!/bin/bash

# KMRL Document Intelligence MVP - Setup Test Script

echo "🚀 KMRL Document Intelligence MVP Setup Test"
echo "============================================="

# Function to check if a service is running
check_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1

    echo "⏳ Checking $service_name..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo "✅ $service_name is running!"
            return 0
        fi
        echo "   Attempt $attempt/$max_attempts - waiting for $service_name..."
        sleep 2
        ((attempt++))
    done
    
    echo "❌ $service_name failed to start within timeout"
    return 1
}

# Start Docker Compose services
echo "🐳 Starting Docker Compose services..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

echo ""
echo "🔍 Checking service health..."

# Check all services
check_service "http://localhost:8000/health" "Backend API"
check_service "http://localhost:3000" "Frontend"
check_service "http://localhost:9000/minio/health/live" "MinIO"
check_service "http://localhost:6333/health" "Qdrant"

# Check if Redis is accessible
echo "⏳ Checking Redis..."
if docker compose exec -T redis redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis is running!"
else
    echo "❌ Redis is not responding"
fi

# Check if PostgreSQL is accessible
echo "⏳ Checking PostgreSQL..."
if docker compose exec -T postgres pg_isready -U kmrl_user | grep -q "accepting connections"; then
    echo "✅ PostgreSQL is running!"
else
    echo "❌ PostgreSQL is not ready"
fi

echo ""
echo "📊 Service URLs:"
echo "- Frontend:        http://localhost:3000"
echo "- Backend API:     http://localhost:8000"
echo "- API Docs:        http://localhost:8000/docs"
echo "- MinIO Console:   http://localhost:9001"
echo "- Qdrant Dashboard: http://localhost:6333/dashboard"

echo ""
echo "🧪 Testing API endpoints..."

# Test health endpoint
if curl -s "http://localhost:8000/health" | grep -q "healthy"; then
    echo "✅ Health endpoint working"
else
    echo "❌ Health endpoint failed"
fi

# Test API info endpoint
if curl -s "http://localhost:8000/api/info" | grep -q "KMRL"; then
    echo "✅ API info endpoint working"
else
    echo "❌ API info endpoint failed"
fi

# Test service status endpoint
if curl -s "http://localhost:8000/api/status" | grep -q "healthy"; then
    echo "✅ Service status endpoint working"
else
    echo "❌ Service status endpoint failed"
fi

echo ""
echo "🎉 Setup test completed!"
echo ""
echo "📝 Next steps:"
echo "1. Open http://localhost:3000 to see the frontend"
echo "2. Open http://localhost:8000/docs to explore the API"
echo "3. Check the README.md for detailed documentation"
echo ""
echo "🛠️ To view logs: docker compose logs -f"
echo "🛑 To stop all services: docker compose down"
