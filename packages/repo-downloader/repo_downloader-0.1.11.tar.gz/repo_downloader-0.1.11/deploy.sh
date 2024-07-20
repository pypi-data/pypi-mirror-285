#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# Run tests
echo "Running tests..."
pytest

# If tests pass, build the package
if [ $? -eq 0 ]; then
    echo "Tests passed. Building package..."
    python -m build
else
    echo "Tests failed. Aborting build."
    exit 1
fi

# If build succeeds, upload to PyPI
if [ $? -eq 0 ]; then
    echo "Build successful. Uploading to PyPI..."
    twine upload dist/*
else
    echo "Build failed. Aborting upload."
    exit 1
fi

echo "Process completed successfully!"