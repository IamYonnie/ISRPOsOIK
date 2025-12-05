@echo off
REM Script to install Python 3.11 on Windows

echo ========================================
echo Installing Python 3.11...
echo ========================================

REM Try to download Python 3.11 installer from python.org
REM Alternatively, if you have winget:
winget install Python.Python.3.11

if %ERRORLEVEL% EQU 0 (
    echo Python 3.11 installed successfully!
    python3.11 --version
) else (
    echo Failed to install Python 3.11
    echo Please install manually from https://www.python.org/downloads/
    echo Download Python 3.11 and add to PATH
)

pause
