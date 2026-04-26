# Setup AI Service Script
Write-Host "Setting up AI Service..." -ForegroundColor Green

Set-Location ai-service

# Create venv if not exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "`nAI Service setup complete!" -ForegroundColor Green
Write-Host "To run: uvicorn app.main:app --reload --port 8001" -ForegroundColor Cyan
