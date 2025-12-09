#!/bin/bash
set -e

echo "Cloning fixed version to temporary directory..."
cd /tmp
rm -rf healthchain-fixed
git clone https://github.com/dotimplement/HealthChain.git healthchain-fixed
cd healthchain-fixed
git checkout 4e8a666ad25fe3b7229362ed8bbc45f9283e8f51

echo "Copying fixed version to /app..."
rm -rf /app/*
rm -rf /app/.[!.]*  # Remove hidden files except . and ..
cp -r /tmp/healthchain-fixed/. /app/

echo "Cleaning up..."
cd /app
rm -rf .git  # Remove git history
rm -rf /tmp/healthchain-fixed

echo "Installing dependencies with Poetry (fresh virtualenv)..."
rm -rf .venv
poetry config virtualenvs.in-project true
poetry install --no-interaction --no-ansi --with dev

echo "✓ Solution complete: Prefetch model removed, loaders refactored"