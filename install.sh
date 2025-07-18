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


# --- Symlink for Custom Base Command ---
if [ "$BASE_CMD" != "contest-manager" ]; then
  BIN_PATH="$(command -v contest-manager)"
  if [ -n "$BIN_PATH" ]; then
    ln -sf "$BIN_PATH" "/usr/local/bin/$BASE_CMD"
    echo "🔗 Symlink created: /usr/local/bin/$BASE_CMD -> $BIN_PATH"
  else
    echo "⚠️  contest-manager binary not found. Symlink not created."
  fi
fi

# --- Final Instructions ---
echo "🎉✅ Setup complete! You can now use $BASE_CMD CLI commands."
echo ""
echo "👉 Usage:"
echo "   $BASE_CMD --help         # Show all commands"
echo "   sudo $BASE_CMD setup     # Set up contest user and environment"
echo "   sudo $BASE_CMD restrict  # Apply contest restrictions"
echo "   $BASE_CMD status         # Check restriction status"
echo "   sudo $BASE_CMD unrestrict # Remove restrictions"