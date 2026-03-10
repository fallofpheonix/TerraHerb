#!/bin/bash
# Terraherb AI Health Check Script
# Verifies the integrity of the Python AI/ML development environment.
# Usage: ./scripts/check-health.sh [--skip-tests]

set -euo pipefail

SKIP_TESTS="${1:-}"
PASS=0
FAIL=0

if [ -x "venv/bin/python" ]; then
    PYTHON_BIN="venv/bin/python"
    PIP_BIN="venv/bin/pip"
else
    PYTHON_BIN="${PYTHON_BIN:-python3}"
    PIP_BIN="${PIP_BIN:-$(command -v pip || command -v pip3 || true)}"
fi

ok()   { echo "[OK] $1"; PASS=$((PASS + 1)); }
warn() { echo "[WARN] $1"; }
fail() { echo "[FAIL] $1"; FAIL=$((FAIL + 1)); }

echo "Starting Terraherb AI Health Check..."
echo "----------------------------------------"

# Runtime
if command -v "$PYTHON_BIN" > /dev/null 2>&1; then
    ok "Python is installed ($($PYTHON_BIN --version 2>&1))"
else
    fail "Python is MISSING"
fi

if [ -n "$PIP_BIN" ] && command -v "$PIP_BIN" > /dev/null 2>&1; then
    ok "pip is installed ($($PIP_BIN --version 2>&1 | cut -d' ' -f1-2))"
else
    fail "pip is MISSING"
fi

# Package installation
if "$PYTHON_BIN" -c "import terraherb" > /dev/null 2>&1; then
    ok "terraherb package is accessible"
else
    warn "terraherb package NOT found in Python path - run: pip install -e ."
fi

for pkg in torch torchvision cv2 fastapi uvicorn requests pytest yaml PIL; do
    if "$PYTHON_BIN" -c "import $pkg" > /dev/null 2>&1; then
        ok "$pkg is available"
    else
        fail "$pkg is MISSING - run: pip install -r requirements.txt"
    fi
done

# Repository structure
echo ""
echo "-- Repository structure --"
for path in \
    "docs" \
    "configs/default_training.yaml" \
    "terraherb/api/main.py" \
    "terraherb/models/mobilenet_classifier.py" \
    "terraherb/inference/classifier.py" \
    "terraherb/inference/predict.py" \
    "terraherb/knowledge/client.py" \
    "terraherb/training/train_model.py" \
    "terraherb/datasets/plantvillage_loader.py" \
    "tests/test_model.py" \
    "tests/test_inference.py" \
    "tests/test_api.py"; do
    if [ -e "$path" ]; then
        ok "$path exists"
    else
        fail "$path is MISSING"
    fi
done

# Data directories
echo ""
echo "-- Data directories --"
for dir in "datasets_substrate/raw" "datasets_substrate/processed" "datasets_substrate/external" "models/saved"; do
    if [ -d "$dir" ]; then
        ok "$dir exists"
    else
        warn "$dir does not exist - run setup or ingestion scripts"
    fi
done

# Dataset presence
if [ -d "datasets_substrate/raw/plant_disease_merged" ] && [ "$(ls -A datasets_substrate/raw/plant_disease_merged 2>/dev/null)" ]; then
    ok "PlantVillage dataset found in datasets_substrate/raw/plant_disease_merged"
else
    warn "PlantVillage dataset not found - run: python -m terraherb.scripts.ingest_data"
fi

# Saved model
if [ -f "models/saved/mobilenet_v2.pth" ]; then
    ok "Trained model weights found at models/saved/mobilenet_v2.pth"
else
    warn "No trained weights at models/saved/mobilenet_v2.pth - run training first"
fi

# Test suite
if [ "$SKIP_TESTS" != "--skip-tests" ]; then
    echo ""
    echo "-- Running unit tests --"
    if "$PYTHON_BIN" -m pytest tests/ -v --tb=short 2>&1; then
        ok "All tests passed"
    else
        fail "Some tests failed - see output above"
    fi
fi

# Summary
echo ""
echo "----------------------------------------"
echo "Health Check Complete - $PASS passed | $FAIL failed"
if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
