#!/usr/bin/env bash
set -e
cd backend

echo "==> Seeding demo data (skipped if already present)..."
python seed.py

echo "==> Starting ChaiSaathi AI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
