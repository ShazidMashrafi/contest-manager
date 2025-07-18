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


REQ_FILE="requirements.txt"
if [ -f "$REQ_FILE" ]; then
  echo "� Installing Python requirements..."
  pip3 install --break-system-packages -r "$REQ_FILE"
else
  echo "⚠️  $REQ_FILE not found. Skipping Python requirements install."
fi

# --- Uninstall Previous Package ---
echo "🔄 [Step 1/2] Uninstalling previous $PKG_NAME package (if any)..."
if pip3 show $PKG_NAME > /dev/null 2>&1; then
  echo "🗑️  Removing old $PKG_NAME..."
  pip3 uninstall --break-system-packages -y $PKG_NAME
else
  echo "✅ No previous installation of $PKG_NAME found."
fi

# --- Install Package ---
echo "🛠️  [Step 2/2] Installing $PKG_NAME ..."
pip3 install --break-system-packages -e .

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
