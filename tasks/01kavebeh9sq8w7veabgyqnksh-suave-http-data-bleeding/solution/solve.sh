#!/bin/bash
set -e

cd /app

# Re-initialize git (removed in Dockerfile to prevent agents browsing history)
git init
git remote add origin https://github.com/SuaveIO/suave.git

# Fetch the architectural fix commit (includes both SocketTask flush AND separate buffers)
git fetch origin cd515a10305e951166e08fff0fc238e51ca16b03 --depth=1

# Checkout fix commit (-f forces overwrite of untracked files)
git checkout -f cd515a10305e951166e08fff0fc238e51ca16b03

# Rebuild with the fix
dotnet build Suave.sln

echo "✓ Solution applied: HTTP data bleeding fix implemented"