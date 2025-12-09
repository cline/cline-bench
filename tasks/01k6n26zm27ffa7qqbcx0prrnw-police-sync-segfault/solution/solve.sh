#!/bin/bash
set -e
cd /app

echo "Re-initializing git to fetch fix..."
git init
git remote add origin https://github.com/AndreasThinks/your-police-events.git

echo "Fetching and checking out fixed version..."
git fetch origin b39c3feaac22bc660bb72d24e5378dae3eb2b593 --depth=1
git checkout -f b39c3feaac22bc660bb72d24e5378dae3eb2b593

echo "✓ Solution complete!"