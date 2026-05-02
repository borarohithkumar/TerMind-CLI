#!/bin/bash

echo "========================================"
echo "   Installing TerMind Cloud CLI..."
echo "========================================"

# 1. Detect Environment (Termux vs Standard Linux)
if [ -n "$TERMUX_VERSION" ]; then
    echo "📱 Termux Android environment detected!"
    pkg update -y && pkg install python git -y
    BIN_DIR="$PREFIX/bin"
else
    echo "🐧 Standard Linux environment detected!"
    BIN_DIR="$HOME/.local/bin"
    mkdir -p "$BIN_DIR"
fi

INSTALL_DIR="$HOME/.termind"

# 2. Create system directories
echo "📁 Setting up directories..."
rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# 3. Copy the client
cp client/termind.py "$INSTALL_DIR/termind.py"

# 4. Set up the secure Python environment
echo "⚙️ Building isolated Machine Learning bridge..."
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install requests --quiet

# 5. Create the global executable command
WRAPPER_SCRIPT="$BIN_DIR/termind"
cat << EOF > "$WRAPPER_SCRIPT"
#!/bin/bash
"$INSTALL_DIR/venv/bin/python" "$INSTALL_DIR/termind.py" "\$@"
EOF
chmod +x "$WRAPPER_SCRIPT"

# 6. ZSH / Bash PATH Auto-Fixer (Standard Linux Only)
if [ -z "$TERMUX_VERSION" ]; then
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo "🔧 Fixing Shell PATH for ~/.local/bin..."
        if [ -f "$HOME/.zshrc" ]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
            echo "✅ Added to .zshrc"
        elif [ -f "$HOME/.bashrc" ]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
            echo "✅ Added to .bashrc"
        fi
    fi
fi

echo "========================================"
echo " ✅ Installation Complete!"
echo " ⚠️ IMPORTANT: You MUST run 'source ~/.zshrc' or open a NEW terminal tab!"
echo " Then, simply type: termind"
echo "========================================"
