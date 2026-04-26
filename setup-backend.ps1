# Setup Backend Script
Write-Host "Setting up Backend..." -ForegroundColor Green

Set-Location backend

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

Write-Host "`nBackend setup complete!" -ForegroundColor Green
Write-Host "To run: uvicorn app.main:app --reload --port 8000" -ForegroundColor Cyan
