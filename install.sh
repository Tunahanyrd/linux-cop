#!/bin/bash
set -e

echo " Linux-Cop installation is starting..."

echo " Installing LinuxCop from GitHub..."

if [ ! -d "linux-cop" ]; then
    echo "📦 Downloading latest version from GitHub..."
    git clone https://github.com/Tunahanyrd/linux-cop.git
    cd linux-cop
else
    echo " linux-cop directory already exists."
    cd linux-cop
fi

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

if [ ! -d "fastfetch" ]; then
    echo " NOTE: Fastfetch was not found. Please ensure the agent runs stably."
fi

source venv/bin/activate

echo "Installing dependencies from requirements.txt..."
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo " requirements.txt was not found. Please check your installation."
fi

ALIAS_CMD="alias cop='python3 $(pwd)/app.py'"
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
echo " cop session"
