#!/bin/bash
set -e

echo " Linux-Cop installation is starting..."

if ! command -v python3 &> /dev/null; then
    echo " Python3 was not found."
    echo "Please install it first and then try running the script again."
    exit 1
else
    echo " Python3 was found: $(python3 --version)"
fi

if [ ! -d "venv" ]; then
    echo " Python venv is being created..."
    python3 -m venv venv
else 
    echo " Venv was found."
fi

source venv/bin/activate

echo "Installing dependencies from requirements.txt..."
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo " requirements.txt was not found. Please check your installation."
fi

ALIAS_CMD="alias cop='bash $(pwd)/app.py'"
if ! grep -q "alias cop=" ~/.bashrc; then
    echo "$ALIAS_CMD" >> ~/.bashrc
    echo "'cop' command was added to .bashrc file."
else
    echo "'cop' alias already defined."
fi

echo ""
echo " Setup complete!"
echo "Restart the terminal or run this:"
echo "  source ~/.bashrc"
echo ""
echo "Now you can type this:"
echo "  cop session"
