#!/bin/bash
set -e

cd /app

# Remove old directories that will be replaced by git checkout
# (prevents both telegram-source and telegram from existing)
rm -rf plugins/telegram-source

# Re-initialize git (removed in Dockerfile to prevent history browsing)
git init
git remote add origin https://github.com/near-everything/every-plugin.git

# Fetch and checkout the fixed commit
git fetch origin 433e4ba6fb90bd8224a129c6ba85130db744c547 --depth=1
git checkout -f 433e4ba6fb90bd8224a129c6ba85130db744c547

# Reinstall dependencies with the updated package.json
bun install

# Build the monorepo (needed for compilation test)
bun run build

echo "✓ Migration to promise-based runtime API complete!"