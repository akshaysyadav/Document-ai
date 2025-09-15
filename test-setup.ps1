# KMRL Document Intelligence MVP - Setup Test Script (PowerShell)

Write-Host "KMRL Document Intelligence MVP Setup Test" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Function to check if a service is running
function Test-Service {
    param(
        [string]$Url,
        [string]$ServiceName,
        [int]$MaxAttempts = 30
    )
    
    Write-Host "Checking $ServiceName..." -ForegroundColor Yellow
    
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "[OK] $ServiceName is running!" -ForegroundColor Green
                return $true
            }
        }
        catch {
            # Continue trying
        }
        
        Write-Host "   Attempt $attempt/$MaxAttempts - waiting for $ServiceName..." -ForegroundColor Gray
        Start-Sleep -Seconds 2
    }
    
    Write-Host "[FAIL] $ServiceName failed to start within timeout" -ForegroundColor Red
    return $false
}

# Start Docker Compose services
Write-Host "Starting Docker Compose services..." -ForegroundColor Blue
docker compose up -d

Write-Host ""
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "Checking service health..." -ForegroundColor Blue

# Check all services
$backendOk = Test-Service -Url "http://localhost:8000/health" -ServiceName "Backend API"
$frontendOk = Test-Service -Url "http://localhost:3000" -ServiceName "Frontend"
$minioOk = Test-Service -Url "http://localhost:9000/minio/health/live" -ServiceName "MinIO"
$qdrantOk = Test-Service -Url "http://localhost:6333/health" -ServiceName "Qdrant"

# Check Redis
Write-Host "Checking Redis..." -ForegroundColor Yellow
try {
    $redisResult = docker compose exec -T redis redis-cli ping 2>$null
    if ($redisResult -match "PONG") {
        Write-Host "[OK] Redis is running!" -ForegroundColor Green
        $redisOk = $true
    } else {
        Write-Host "[FAIL] Redis is not responding" -ForegroundColor Red
        $redisOk = $false
    }
}
catch {
    Write-Host "[FAIL] Redis check failed" -ForegroundColor Red
    $redisOk = $false
}

# Check PostgreSQL
Write-Host "Checking PostgreSQL..." -ForegroundColor Yellow
try {
    $pgResult = docker compose exec -T postgres pg_isready -U kmrl_user 2>$null
    if ($pgResult -match "accepting connections") {
        Write-Host "[OK] PostgreSQL is running!" -ForegroundColor Green
        $pgOk = $true
    } else {
        Write-Host "[FAIL] PostgreSQL is not ready" -ForegroundColor Red
        $pgOk = $false
    }
}
catch {
    Write-Host "[FAIL] PostgreSQL check failed" -ForegroundColor Red
    $pgOk = $false
}

Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Cyan
Write-Host "- Frontend:         http://localhost:3000" -ForegroundColor White
Write-Host "- Backend API:      http://localhost:8000" -ForegroundColor White
Write-Host "- API Docs:         http://localhost:8000/docs" -ForegroundColor White
Write-Host "- MinIO Console:    http://localhost:9001" -ForegroundColor White
Write-Host "- Qdrant Dashboard: http://localhost:6333/dashboard" -ForegroundColor White

Write-Host ""
Write-Host "Testing API endpoints..." -ForegroundColor Blue

$apiTestsOk = $true

# Test health endpoint
try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10
    if ($healthResponse.status -eq "healthy") {
        Write-Host "[OK] Health endpoint working" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Health endpoint failed" -ForegroundColor Red
        $apiTestsOk = $false
    }
}
catch {
    Write-Host "[FAIL] Health endpoint failed" -ForegroundColor Red
    $apiTestsOk = $false
}

# Test API info endpoint
try {
    $infoResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/info" -TimeoutSec 10
    if ($infoResponse.name -match "KMRL") {
        Write-Host "[OK] API info endpoint working" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] API info endpoint failed" -ForegroundColor Red
        $apiTestsOk = $false
    }
}
catch {
    Write-Host "[FAIL] API info endpoint failed" -ForegroundColor Red
    $apiTestsOk = $false
}

# Test service status endpoint
try {
    $statusResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/status" -TimeoutSec 10
    if ($statusResponse.api -eq "healthy") {
        Write-Host "[OK] Service status endpoint working" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Service status endpoint failed" -ForegroundColor Red
        $apiTestsOk = $false
    }
}
catch {
    Write-Host "[FAIL] Service status endpoint failed" -ForegroundColor Red
    $apiTestsOk = $false
}

Write-Host ""
Write-Host "Setup test completed!" -ForegroundColor Green

# Summary
$allOk = $backendOk -and $frontendOk -and $minioOk -and $qdrantOk -and $redisOk -and $pgOk -and $apiTestsOk

if ($allOk) {
    Write-Host "[SUCCESS] All services are running successfully!" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Some services may have issues. Check the logs for details." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Open http://localhost:3000 to see the frontend" -ForegroundColor White
Write-Host "2. Open http://localhost:8000/docs to explore the API" -ForegroundColor White
Write-Host "3. Check the README.md for detailed documentation" -ForegroundColor White
Write-Host ""
Write-Host "To view logs: docker compose logs -f" -ForegroundColor Yellow
Write-Host "To stop all services: docker compose down" -ForegroundColor Yellow
