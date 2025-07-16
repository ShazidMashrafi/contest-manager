#!/bin/bash
# 🚀 Contest Environment Manager Installer
set -e

# --- Config ---
BASE_CMD="contest-manager"
if [ -n "$1" ]; then
  BASE_CMD="$1"
fi
PKG_NAME="contest-environment-manager"

# --- Root Check ---
if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run as root: sudo $0"
  exit 1
fi

# --- Install System Requirements---
if [ -f requirements/system-requirements.txt ]; then
  echo "🔧 Installing system requirements..."
  grep -v '^#' requirements/system-requirements.txt | xargs -r apt-get install -y
else
  echo "⚠️  requirements/system-requirements.txt not found. Skipping system requirements install."
fi

# --- Uninstall Previous Package ---
echo "🔄 [1/2] Uninstalling previous $PKG_NAME package (if any)..."
if pip3 show $PKG_NAME > /dev/null 2>&1; then
  echo "🗑️  Removing old $PKG_NAME..."
  pip3 uninstall --break-system-packages -y $PKG_NAME
else
  echo "✅ No previous installation of $PKG_NAME found."
fi

# --- Install Dependencies & Package ---
echo "📦 [2/2] Installing $PKG_NAME dependencies..."
pip3 install --break-system-packages -r requirements/requirements.txt
echo "🛠️  Installing $PKG_NAME in editable mode..."
pip3 install --break-system-packages -e .

# --- Create Custom CLI Symlink ---
if [ "$BASE_CMD" != "contest-manager" ]; then
  BIN_PATH="$(command -v contest-manager)"
  if [ -n "$BIN_PATH" ]; then
    ln -sf "$BIN_PATH" "/usr/local/bin/$BASE_CMD"
    echo "🔗 Symlink created: $BASE_CMD -> contest-manager"
  else
    echo "⚠️  contest-manager CLI not found in PATH. Symlink not created."
  fi
fi

# --- Final Instructions ---
echo "🎉✅ Setup complete! You can now use $BASE_CMD CLI commands."
echo ""
echo "👉 Usage:"
echo "   $BASE_CMD --help      # Show all commands"
echo "   sudo $BASE_CMD setup  # Set up contest user and environment"
echo "   sudo $BASE_CMD restrict  # Apply contest restrictions"
echo "   $BASE_CMD status      # Check restriction status"
echo "   sudo $BASE_CMD unrestrict # Remove restrictions"
