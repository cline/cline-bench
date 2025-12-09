#!/bin/bash
set -e

cd /app

# Re-initialize git to fetch the fix commit
git init
git remote add origin https://github.com/Wetdogtaste/Film-Archiver.git

# Fetch the fix commit (v1.2.1)
git fetch origin 928fa124d0baf7302aa0284a5833236ace90e536 --depth=1

# Checkout the fix - use -f to force overwrite untracked files
git checkout -f 928fa124d0baf7302aa0284a5833236ace90e536

echo "✓ Solution applied: v1.2.1 fixes"
echo "  - Phantom tk window fix (lazy import in main.py)"
echo "  - DMG installer UX improvement (background image + visual guide)"