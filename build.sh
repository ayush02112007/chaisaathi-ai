#!/usr/bin/env bash
set -e

echo "==> Building React frontend..."
npm --prefix frontend install
npm --prefix frontend run build

echo "==> Copying frontend build into backend/static..."
mkdir -p backend/static
cp -r frontend/dist/* backend/static/

echo "==> Installing Python dependencies..."
pip install -r backend/requirements.txt

echo "==> Build complete."
