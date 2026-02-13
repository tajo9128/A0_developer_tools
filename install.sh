#!/bin/bash
# Install script for Elite Developer Tools skill

# Copy tools to Agent Zero tools directory
TOOLS_DEST="/a0/python/tools"
if [ -d "$TOOLS_DEST" ]; then
    cp tools/*.py "$TOOLS_DEST/"
    echo "Tools copied to $TOOLS_DEST"
else
    echo "Error: Tools directory $TOOLS_DEST not found. Adjust path as needed."
    exit 1
fi

# Install dependencies
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "Dependencies installed"
else
    echo "requirements.txt not found"
fi

echo "Installation complete. Restart Agent Zero to load the skill."
