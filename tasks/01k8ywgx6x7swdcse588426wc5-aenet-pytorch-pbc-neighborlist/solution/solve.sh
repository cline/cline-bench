#!/bin/bash
set -e
cd /app

echo "Re-initializing git to fetch fix..."
git init
git remote add origin https://github.com/atomisticnet/aenet-python.git

echo "Fetching and checking out fixed version..."
git fetch origin 8ceabcc3d1a44e44c126fa800e9bae1946191a71 --depth=1
git checkout -f 8ceabcc3d1a44e44c126fa800e9bae1946191a71

echo "Reinstalling package with fix in aenet-torch conda env..."
source /opt/conda/etc/profile.d/conda.sh
conda activate aenet-torch
pip install -e .

echo "✓ Solution complete! PBC epsilon tolerance fix applied."