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

# --- Ensure apt-get is available and update package lists ---
echo "🔧 Updating system package lists..."
apt-get update -qq || apt-get update

# --- Ensure python3 and python3-pip are installed ---
echo "📦 Ensuring python3 and python3-pip are installed..."
if ! command -v python3 >/dev/null 2>&1; then
  echo "   Installing python3..."
  apt-get install -y python3 || { echo "❌ Failed to install python3"; exit 1; }
fi

if ! command -v pip3 >/dev/null 2>&1 && ! python3 -m pip --version >/dev/null 2>&1; then
  echo "   Installing python3-pip..."
  apt-get install -y python3-pip || apt-get install -y python3-distutils python3-dev && python3 -m ensurepip --default-pip || true
fi

# Use python3 -m pip for reliability
PIP_BIN="python3 -m pip"

# --- Final pip availability check ---
if ! $PIP_BIN --version >/dev/null 2>&1; then
  echo "❌ Failed to install or find pip for python3."
  echo "💡 Troubleshooting:"
  echo "    1. sudo apt-get update"
  echo "    2. sudo apt-get install -y python3-pip"
  echo "    3. sudo python3 -m pip install --upgrade pip"
  exit 1
fi

echo "✅ Python3 and pip are available:"
python3 --version
$PIP_BIN --version

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
  # If PIP_BREAK_FLAG is empty the expansion yields nothing
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
# -e . is used for editable install during development
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
