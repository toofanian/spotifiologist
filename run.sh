#!/bin/bash

# Use the Python from the spotifiologist environment
PYTHON_PATH="/Users/alextoofanian/opt/miniconda3/envs/spotifiologist/bin/python"

# Check if the Python interpreter exists
if [ ! -f "$PYTHON_PATH" ]; then
    echo "Error: Python interpreter not found at $PYTHON_PATH"
    echo "Make sure the spotifiologist conda environment is created"
    exit 1
fi

# Run the script with the correct Python
exec "$PYTHON_PATH" "$@"
