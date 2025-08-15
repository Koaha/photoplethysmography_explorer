@echo off
REM Documentation build script for Windows
REM PPG Analysis Tool

echo 🚀 PPG Analysis Tool - Documentation Builder
echo ================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python not found in PATH
    echo Please install Python and add it to your PATH
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "docs" (
    echo ❌ Error: docs/ directory not found!
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

REM Build documentation
echo 🔨 Building documentation...
python build_docs.py

if errorlevel 1 (
    echo.
    echo 💥 Documentation build failed!
    pause
    exit /b 1
) else (
    echo.
    echo 🎉 Documentation build completed successfully!
    echo You can now open docs\_build\html\index.html in your browser
)

pause
