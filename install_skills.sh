#!/bin/bash
# Wrapper to run install_skills.py with python3

# Get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

python3 "$DIR/install_skills.py" "$@"
