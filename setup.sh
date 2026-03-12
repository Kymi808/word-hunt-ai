#!/bin/bash
# Word Hunt AI - Setup Script

set -e

echo "=== Word Hunt AI Setup ==="

# Check Python version
python3 --version || { echo "Python 3 is required. Install from python.org"; exit 1; }

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check for Tesseract (optional, for OCR mode)
if command -v tesseract &> /dev/null; then
    echo "Tesseract OCR: installed"
else
    echo "Tesseract OCR: not found (optional - needed for 'capture' mode)"
    echo "  Install with: brew install tesseract"
fi

# Check accessibility permissions (needed for pyautogui)
echo ""
echo "=== Important: macOS Permissions ==="
echo "For auto-play mode, grant Accessibility permissions to your terminal app:"
echo "  System Settings > Privacy & Security > Accessibility"
echo "  Enable your terminal (Terminal.app, iTerm2, etc.)"
echo ""

echo "Setup complete! Activate the venv with: source venv/bin/activate"
echo "Quick start: python -m src.main solve"
