# Setup Frontend Script
Write-Host "Setting up Frontend..." -ForegroundColor Green

Set-Location frontend

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
npm install

Write-Host "`nFrontend setup complete!" -ForegroundColor Green
Write-Host "To run: npm run dev" -ForegroundColor Cyan
