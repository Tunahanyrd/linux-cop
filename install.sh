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

if [ ! -d "venv" ] || [ ! -f "venv/bin/activate" ]; then
    echo " Python venv is being created (or repaired)..."
    rm -rf venv 2>/dev/null || true
    python3 -m venv venv || {
        echo "❌ Failed to create Python virtual environment. Check your python3-venv package."
        exit 1
    }
else
    echo " ✅ Venv looks healthy."
fi

if ! command -v fastfetch &> /dev/null; then
    echo " ⚠️ Fastfetch not found. You can install it with:"
    echo "    apt install fastfetch"
fi

source venv/bin/activate

echo "Installing dependencies from requirements.txt..."
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo " requirements.txt was not found. Please check your installation."
fi

INSTALL_DIR="$(pwd)"
ALIAS_CMD="alias cop='$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/app.py'"

# Detect shell and add alias to appropriate config file
if [ -n "$FISH_VERSION" ] || [ "$SHELL" = "$(command -v fish)" ]; then
    CONFIG_FILE="$HOME/.config/fish/config.fish"
    mkdir -p "$HOME/.config/fish"
    if ! grep -q "alias cop=" "$CONFIG_FILE" 2>/dev/null; then
        echo "$ALIAS_CMD" >> "$CONFIG_FILE"
        echo "'cop' command was added to config.fish file."
    else
        echo "'cop' alias already defined in fish config."
    fi
elif [ -f "$HOME/.zshrc" ] || [ "$SHELL" = "$(command -v zsh)" ]; then
    CONFIG_FILE="$HOME/.zshrc"
    if ! grep -q "alias cop=" "$CONFIG_FILE"; then
        echo "$ALIAS_CMD" >> "$CONFIG_FILE"
        echo "'cop' command was added to .zshrc file."
    else
        echo "'cop' alias already defined in zsh config."
    fi
else
    CONFIG_FILE="$HOME/.bashrc"
    if ! grep -q "alias cop=" "$CONFIG_FILE"; then
        echo "$ALIAS_CMD" >> "$CONFIG_FILE"
        echo "'cop' command was added to .bashrc file."
    else
        echo "'cop' alias already defined in bash config."
    fi
fi

echo ""
echo " Setup complete!"
echo "Restart the terminal or run this:"
if [ -n "$FISH_VERSION" ] || [ "$SHELL" = "$(command -v fish)" ]; then
    echo "  source ~/.config/fish/config.fish"
elif [ -f "$HOME/.zshrc" ] || [ "$SHELL" = "$(command -v zsh)" ]; then
    echo "  source ~/.zshrc"
else
    echo "  source ~/.bashrc"
fi
echo ""
echo "Now you can type this:"
echo " cop session"
