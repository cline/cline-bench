#!/bin/bash
set -e

cd /app

# Re-initialize git (removed in Dockerfile to prevent agents browsing history)
git init
git remote add origin https://github.com/klogt-as/intercept.git

# Fetch and checkout the fix commit
git fetch origin 052106281c24329e1af1c2dd8cf7adce2752b1d6 --depth=1
git checkout -f 052106281c24329e1af1c2dd8cf7adce2752b1d6

# Install dependencies (in case package.json changed)
pnpm install --frozen-lockfile

# Build the project
pnpm run build

echo "✓ Solution applied: axios adapter now properly throws AxiosError for non-2xx status codes"