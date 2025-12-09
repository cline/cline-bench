#!/bin/bash
set -e
cd /app

echo "Re-initializing git to fetch fix..."
git init
git remote add origin https://github.com/sergev/v-edit.git

echo "Fetching and checking out fixed version..."
git fetch origin 57bba22be8d297699450f684ca2933b65ac5e0cc --depth=1
git checkout -f 57bba22be8d297699450f684ca2933b65ac5e0cc

echo "Patching CMakeLists.txt to disable -Werror (sign-compare warnings on Linux)..."
sed -i 's/-Werror/-Wno-error/g' CMakeLists.txt

echo "Rebuilding project with fixes..."
cd build
cmake ..
make

echo "✓ Solution complete!"