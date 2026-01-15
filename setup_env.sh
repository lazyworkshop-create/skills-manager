#!/bin/bash

echo "Checking environment setup for macOS/Linux..."

# Check Python 3
if command -v python3 &> /dev/null; then
    echo "✓ Python 3 is installed: $(python3 --version)"
else
    echo "✗ Python 3 is NOT installed."
    echo "  Please install Python 3 using your package manager."
    echo "  macOS: brew install python"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip"
    exit 1
fi

# Check Pip
if python3 -m pip --version &> /dev/null; then
    echo "✓ pip is installed."
else
    echo "✗ pip is NOT installed."
    echo "  Please install pip for Python 3."
    exit 1
fi

# Check Git
if command -v git &> /dev/null; then
    echo "✓ git is installed."
else
    echo "✗ git is NOT installed."
    echo "  Please install git."
    exit 1
fi

# Check Python Version Manager (uv or pyenv)
echo "Checking for Python Version Manager..."
if command -v uv &> /dev/null; then
    echo "✓ uv is installed (Recommended)."
elif command -v pyenv &> /dev/null; then
    echo "✓ pyenv is installed."
elif command -v conda &> /dev/null; then
    echo "✓ conda is installed."
else
    echo "✗ No Python version manager found (uv, pyenv, or conda)."
    echo "  We recommend installing 'uv' for fast Python env management:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    # Optional: ask user to install? For now just informational as per request "Add a python version manager" support/check.
fi

echo ""
echo "Environment setup complete. You can now run ./install_skills.sh"
