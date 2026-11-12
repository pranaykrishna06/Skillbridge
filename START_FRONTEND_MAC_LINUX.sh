#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/frontend"
if [ ! -f .env.local ]; then
  echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
fi
if [ ! -d node_modules ]; then
  npm install
fi
npm run dev
