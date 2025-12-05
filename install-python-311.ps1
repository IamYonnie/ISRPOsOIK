# PowerShell script to install Python 3.11 on Windows
# Run as Administrator

Write-Host "========================================" -ForegroundColor Green
Write-Host "Installing Python 3.11..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Check if winget is available
if (Get-Command winget -ErrorAction SilentlyContinue) {
    Write-Host "Using winget to install Python 3.11..." -ForegroundColor Yellow
    winget install Python.Python.3.11
} elseif (Get-Command choco -ErrorAction SilentlyContinue) {
    Write-Host "Using Chocolatey to install Python 3.11..." -ForegroundColor Yellow
    choco install python311
} else {
    Write-Host "Please install Python 3.11 manually:" -ForegroundColor Red
    Write-Host "1. Visit https://www.python.org/downloads/release/python-3110/" -ForegroundColor Yellow
    Write-Host "2. Download 'Windows x86-64 installer' or 'Windows x86 installer'" -ForegroundColor Yellow
    Write-Host "3. Run installer and check 'Add Python 3.11 to PATH'" -ForegroundColor Yellow
    Start-Process "https://www.python.org/downloads/release/python-3110/"
}

# Verify installation
Write-Host ""
Write-Host "Verifying installation..." -ForegroundColor Yellow
python3.11 --version
if ($LASTEXITCODE -eq 0) {
    Write-Host "Python 3.11 installed successfully!" -ForegroundColor Green
    Write-Host "Now run: python3.11 -m venv venv" -ForegroundColor Green
} else {
    Write-Host "Python 3.11 not found in PATH" -ForegroundColor Red
    Write-Host "Please restart PowerShell or add Python 3.11 to PATH manually" -ForegroundColor Red
}
