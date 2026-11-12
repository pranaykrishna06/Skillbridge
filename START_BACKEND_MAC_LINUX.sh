#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/backend"
if [ ! -f .env ]; then
  echo "ERROR: backend/.env missing. Copy .env.example to .env and edit credentials."
  exit 1
fi
if [ ! -d .venv ]; then
  python3.11 -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
