#!/bin/bash
# 🚀 Contest Environment Manager Installer
set -e

# --- Config ---
BASE_CMD="contest-manager"
PKG_NAME="contest-environment-manager"

# --- Root Check ---
if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run as root: sudo $0"
  exit 1
fi

# --- Check pip version for --break-system-packages support ---
PIP_VERSION=$(pip3 --version | grep -oP '\d+\.\d+' | head -1)
PIP_MAJOR=$(echo $PIP_VERSION | cut -d. -f1)
PIP_MINOR=$(echo $PIP_VERSION | cut -d. -f2)

# --break-system-packages added in pip 23.1
if [ "$PIP_MAJOR" -gt 23 ] || ([ "$PIP_MAJOR" -eq 23 ] && [ "$PIP_MINOR" -ge 1 ]); then
  PIP_FLAG="--break-system-packages"
else
  PIP_FLAG=""
  echo "⚠️  pip version $PIP_VERSION is older than 23.1. Skipping --break-system-packages flag."
  echo "💡 To update pip: sudo pip3 install --upgrade pip"
fi

REQ_FILE="requirements.txt"
if [ -f "$REQ_FILE" ]; then
  echo "� Installing Python requirements..."
  pip3 install $PIP_FLAG -r "$REQ_FILE"
else
  echo "⚠️  $REQ_FILE not found. Skipping Python requirements install."
fi

# --- Uninstall Previous Package ---
echo "🔄 [Step 1/2] Uninstalling previous $PKG_NAME package (if any)..."
if pip3 show $PKG_NAME > /dev/null 2>&1; then
  echo "🗑️  Removing old $PKG_NAME..."
  pip3 uninstall $PIP_FLAG -y $PKG_NAME
else
  echo "✅ No previous installation of $PKG_NAME found."
fi

# --- Install Package ---
echo "🛠️  [Step 2/2] Installing $PKG_NAME ..."
pip3 install $PIP_FLAG -e .

# --- Final Instructions ---
echo "🎉✅ Setup complete! You can now use contest-manager CLI commands."
echo ""
echo "👉 Usage:"
echo "   contest-manager --help         # Show all commands"
echo "   sudo contest-manager setup     # Set up contest user and environment"
echo "   sudo contest-manager restrict  # Apply contest restrictions"
echo "   contest-manager status         # Check restriction status"
echo "   sudo contest-manager unrestrict # Remove restrictions"
echo "   sudo contest-manager start-restriction # Start persistent restriction service"
echo "   sudo contest-manager update-restriction # Update persistent restriction service"
