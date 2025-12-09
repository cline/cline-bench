#!/bin/bash
set -e

cd /app

# Re-initialize git (removed in Dockerfile)
git init
git remote add origin https://github.com/jamesmparry87/discord.git

# Fetch the fixed commit
git fetch origin aae294a34043bba654ce1772bc0e3c04ed67efde --depth=1

# Checkout the fix (force overwrite since files are untracked after rm .git)
git checkout -f aae294a34043bba654ce1772bc0e3c04ed67efde

echo "✓ Solution applied: Fixed RealDictCursor KeyError bug in database_module.py"