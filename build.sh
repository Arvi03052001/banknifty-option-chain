#!/bin/bash
set -e

echo "Starting build process..."

# Upgrade pip and build tools
pip install --upgrade pip setuptools wheel

# Install packages with pre-compiled wheels only
pip install --only-binary=all --upgrade \
    Flask \
    requests \
    gunicorn \
    Werkzeug \
    pytz \
    python-dateutil \
    schedule \
    fyers-apiv3

# Try to install numpy and pandas with fallback
echo "Installing numpy..."
pip install --only-binary=numpy "numpy>=1.21.0,<2.0.0" || pip install "numpy>=1.21.0,<2.0.0"

echo "Installing pandas..."
pip install --only-binary=pandas "pandas>=1.5.0,<2.1.0" || pip install "pandas>=1.5.0,<2.1.0"

echo "Build completed successfully!"