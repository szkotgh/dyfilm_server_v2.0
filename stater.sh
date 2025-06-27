#!/bin/bash

DIR="$( cd "$( dirname "$0" )" && pwd -P )"

# Get the path of the script
echo dyfilm server Path=\'$DIR\'
cd "$DIR"

# if git is installed, pull the latest changes
if command -v git &> /dev/null
then
    git pull
else
    echo "dyfilm server git not found, skipping pull . . ."
fi

# Start the server
python3 app.py
