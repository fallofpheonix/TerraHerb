#!/bin/bash

# 🌿 Terraherb AI Health Check Script
# Verifies the integrity of the Python AI/ML development environment.

echo "🌿 Starting Terraherb AI Health Check..."

# Check Python
if command -v python3 > /dev/null; then
    echo "✅ Python 3 is installed."
else
    echo "❌ Python 3 is MISSING."
fi

# Check pip
if command -v pip > /dev/null; then
    echo "✅ pip is installed."
else
    echo "❌ pip is MISSING."
fi

# Check Package Installation
if python3 -c "import terraherb" > /dev/null 2>&1; then
    echo "✅ terraherb package is accessible."
else
    echo "⚠️  terraherb package is NOT in the Python path (ensure you are in the root)."
fi

# Check Core ML Dependencies
for pkg in torch torchvision cv2 fastapi uvicorn requests pytest; do
    if python3 -c "import $pkg" > /dev/null 2>&1; then
        echo "✅ $pkg is available."
    else
        echo "⚠️  $pkg is MISSING (run pip install -r requirements.txt)."
    fi
done

# Run Test Suite
echo "🌿 Running unit tests..."
pytest tests/

# Check Documentation Structure
if [ -d "docs/architecture" ] && [ -d "data/raw" ]; then
    echo "✅ New AI/ML repository structure is valid."
else
    echo "❌ Repository structure is INCOMPLETE."
fi

echo "🌿 Health Check Complete."
