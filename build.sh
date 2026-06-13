#!/usr/bin/env bash
set -euo pipefail

# Build the React SPA into ./static/ which FastAPI serves at /.
echo "── Installing & building frontend ──"
pushd frontend > /dev/null
npm ci
npm run build
popd > /dev/null

echo "── Installing Python dependencies ──"
pip install -r requirements.txt

echo "✓ Build complete."
