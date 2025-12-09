#!/bin/bash

cd /tests

# Run tests directly in the conda environment where aenet is installed
# The Dockerfile already has pytest installed in aenet-torch env
conda run -n aenet-torch pytest test_pbc_forces.py -rA

if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi