#!/bin/zsh

# Source conda.sh to enable conda command
source ~/opt/miniconda3/etc/profile.d/conda.sh

# Activate the environment
conda activate spotifiologist

# Install dependencies
python -m pip install -r requirements.txt

# Print environment info
echo "Python version:"
python --version
echo "\nPython path:"
which python
