#!/bin/bash
# Solution script: Apply user's actual fix from PR #1
# Migrates 4 React components from fetch() to oRPC client

set -e

cd /app

# Re-initialize git (removed in Dockerfile to prevent history browsing)
git init
git remote add origin https://github.com/jlwaugh/neargov.git

# Fetch the merge commit from PR #1
# Commit 1663f4e414e6526ce153be685adf80e71bbf8818 is the merge of PR #1
git fetch origin 1663f4e414e6526ce153be685adf80e71bbf8818 --depth=1

# Apply the fix with -f to force overwrite untracked files
git checkout -f 1663f4e414e6526ce153be685adf80e71bbf8818

# Explicitly delete files that were removed in PR #1
# git checkout -f doesn't delete removed files when they're untracked (after rm -rf .git)
rm -f src/pages/api/discourse/\[\[...orpc\]\].ts

# Fix Navigation case mismatch (pre-existing issue that breaks compilation in Docker)
# _app.tsx imports from @/components/Navigation but file is navigation.tsx (lowercase)
# This prevents compilation on case-sensitive filesystems (Linux/Docker)
sed -i 's/@\/components\/Navigation/@\/components\/navigation/g' src/pages/_app.tsx

# Reinstall dependencies (package.json may have changed)
npm install

# Verify TypeScript types are correct (skip full build - has unrelated SSR issues)
npx tsc --noEmit

echo "✓ Solution applied: 4 components migrated to oRPC client"
echo "  - ConnectDiscourse.tsx: fetch → client.discourse.getUserApiAuthUrl"
echo "  - PublishButton.tsx: fetch → client.discourse.createPost"
echo "  - navigation.tsx: fetch → client.discourse.getLinkage"
echo "  - profile.tsx: fetch → client.discourse.getLinkage"
echo "  - Fixed Navigation import case for compilation"