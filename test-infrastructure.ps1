# Simple Infrastructure Test Script
Write-Host "=== KMRL Infrastructure Test ===" -ForegroundColor Cyan
Write-Host ""

# Check Docker containers
Write-Host "Checking Docker containers..." -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host ""
Write-Host "Testing infrastructure services..." -ForegroundColor Yellow

# Test PostgreSQL
try {
    $pgTest = docker exec kmrl_postgres pg_isready -U kmrl_user 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] PostgreSQL is ready" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] PostgreSQL is not ready" -ForegroundColor Red
    }
} catch {
    Write-Host "[FAIL] PostgreSQL container not found" -ForegroundColor Red
}

# Test Redis
try {
    $redisTest = docker exec kmrl_redis redis-cli ping 2>$null
    if ($redisTest -eq "PONG") {
        Write-Host "[OK] Redis is responding" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Redis is not responding" -ForegroundColor Red
    }
} catch {
    Write-Host "[FAIL] Redis container not found" -ForegroundColor Red
}

# Test MinIO
try {
    $minioTest = Invoke-WebRequest -Uri "http://localhost:9000/minio/health/ready" -TimeoutSec 5 2>$null
    if ($minioTest.StatusCode -eq 200) {
        Write-Host "[OK] MinIO is ready" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] MinIO is not ready" -ForegroundColor Red
    }
} catch {
    Write-Host "[FAIL] MinIO is not accessible" -ForegroundColor Red
}

# Test Qdrant
try {
    $qdrantTest = Invoke-WebRequest -Uri "http://localhost:6333/collections" -TimeoutSec 5 2>$null
    if ($qdrantTest.StatusCode -eq 200) {
        Write-Host "[OK] Qdrant is ready" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Qdrant is not ready" -ForegroundColor Red
    }
} catch {
    Write-Host "[FAIL] Qdrant is not accessible" -ForegroundColor Red
}

Write-Host ""
Write-Host "Infrastructure test completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next: Start the backend and frontend manually" -ForegroundColor Cyan
