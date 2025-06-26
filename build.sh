#!/bin/bash
set -e

echo "Starting build process..."

# Upgrade pip and build tools
pip install --upgrade pip setuptools wheel

# Install from minimal requirements file
echo "Installing from requirements-minimal.txt..."
pip install -r requirements-minimal.txt

echo "Build completed successfully!"