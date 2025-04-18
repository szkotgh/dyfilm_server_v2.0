#!bin/bash

DIR="$( cd "$( dirname "$0" )" && pwd -P )"

# Get the path of the script
echo dyfilm server Path=\'$DIR\'
cd "$DIR"

# Check if the script is running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "dyfilm server stater must be run as root."
    echo "Try 'sudo bash $0'"
    exit 1
fi

# if git is installed, pull the latest changes
if command -v git &> /dev/null
then
    git pull
else
    echo "dyfilm server git not found, skipping pull . . ."
fi

# Start the server
sudo python3 app.py