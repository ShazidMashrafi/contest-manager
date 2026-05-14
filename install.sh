#!/bin/bash
# 🚀 Contest Environment Manager Installer (Ubuntu 22.04+ compatible)
set -euo pipefail

# --- Config ---
BASE_CMD="contest-manager"
PKG_NAME="contest-environment-manager"

# --- Root Check ---
if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run as root: sudo $0"
  exit 1
fi

# --- Ensure python3 exists ---
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ python3 not found. Install python3 and python3-pip first."
  exit 1
fi

# Use python3 -m pip for reliability
PIP_BIN="python3 -m pip"

# --- Check pip availability ---
if ! $PIP_BIN --version >/dev/null 2>&1; then
  echo "⚠️  pip for python3 not found. You can install it with:"
  echo "    sudo apt update && sudo apt install -y python3-pip"
  exit 1
fi

# --- Decide whether to use --break-system-packages (only available in newer pip) ---
if $PIP_BIN install --help 2>&1 | grep -q -- '--break-system-packages'; then
  PIP_BREAK_FLAG="--break-system-packages"
else
  PIP_BREAK_FLAG=""
fi

echo "ℹ️  Using: $PIP_BIN"
if [ -n "$PIP_BREAK_FLAG" ]; then
  echo "ℹ️  pip supports $PIP_BREAK_FLAG; it will be passed to install/uninstall commands."
else
  echo "ℹ️  pip does NOT support --break-system-packages on this system. Proceeding without it."
  echo "    (This is expected on older pip versions such as the default on Ubuntu 22.04.)"
fi

REQ_FILE="requirements.txt"
if [ -f "$REQ_FILE" ]; then
  echo "📦 Installing Python requirements from $REQ_FILE..."
  $PIP_BIN install $PIP_BREAK_FLAG -r "$REQ_FILE"
else
  echo "⚠️  $REQ_FILE not found. Skipping Python requirements install."
fi

# --- Uninstall Previous Package ---
echo "🔄 [Step 1/2] Uninstalling previous $PKG_NAME package (if any)..."
if $PIP_BIN show "$PKG_NAME" >/dev/null 2>&1; then
  echo "🗑️  Removing old $PKG_NAME..."
  $PIP_BIN uninstall $PIP_BREAK_FLAG -y "$PKG_NAME"
else
  echo "✅ No previous installation of $PKG_NAME found."
fi

# --- Install Package (editable) ---
echo "🛠️  [Step 2/2] Installing $PKG_NAME (editable)..."
$PIP_BIN install $PIP_BREAK_FLAG -e .

# --- Final Instructions ---
echo ""
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
echo ""
echo "ℹ️  Notes:"
echo " - On Ubuntu 22.04 the system pip may be an older version that doesn't support"
echo "   --break-system-packages; the script auto-detected and omitted it."
echo " - If you prefer a safer approach that doesn't touch system site-packages, consider"
echo "   using a virtual environment (venv) or running the installer as a non-root user"
echo "   and installing with --user."
echo " - To upgrade pip (optional):"
echo "     sudo python3 -m pip install --upgrade pip"
