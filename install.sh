#!/bin/bash
# 🚀 Contest Environment Manager Installer
set -e

# --- Config ---
BASE_CMD="contest-manager"

# --- Root Check ---
if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run as root: sudo $0"
  exit 1
fi

# --- Check and Install Python3 & pip3 ---
echo "🔍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
  echo "📥 Python3 not found. Installing..."
  apt-get update -qq
  apt-get install -y python3 python3-pip python3-venv
  echo "✅ Python3 and pip3 installed."
else
  echo "✅ Python3 found: $(python3 --version)"
fi

if ! command -v pip3 &> /dev/null; then
  echo "📥 pip3 not found. Installing..."
  apt-get install -y python3-pip
  echo "✅ pip3 installed."
else
  echo "✅ pip3 found: $(pip3 --version)"
fi

# --- Upgrade pip ---
echo "📦 Upgrading pip to latest version..."
pip3 install --upgrade pip

REQ_FILE="requirements.txt"
if [ -f "$REQ_FILE" ]; then
  echo "📦 Installing Python requirements from $REQ_FILE..."
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