#!/bin/bash
set -e
cd /app

echo "Re-initializing git to fetch fix..."
git init
git remote add origin https://github.com/near-everything/every-plugin.git

echo "Fetching and checking out fixed version..."
git fetch origin 0f98ec19d10afe4d72b15aee9fe1c2f2a4ab63cd --depth=1
git checkout -f 0f98ec19d10afe4d72b15aee9fe1c2f2a4ab63cd

echo "Installing dependencies for fixed version..."
bun install

echo "Building project..."
bun run build

echo "✓ Solution complete!"