#!/usr/bin/env bash
# CryptoScope startup script
set -euo pipefail

echo "=== CryptoScope ==="
echo "Starting on port 8010..."

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing dependencies..."
pip install -q -r requirements.txt

echo "Starting CryptoScope..."
python app.py
