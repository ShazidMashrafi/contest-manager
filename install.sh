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



# --- Step 1: Install System Requirements ---
echo "\n🧩 STEP 1: Install System Requirements\n========================================"
if [ -f requirements/system-requirements.txt ]; then
  grep -v '^#' requirements/system-requirements.txt | xargs -r apt-get install -y
else
  echo "⚠️  requirements/system-requirements.txt not found. Skipping system requirements install."
fi

# --- Step 2: Install Python Requirements ---
echo "\n🐍 STEP 2: Install Python Requirements\n========================================"
REQ_FILE="requirements/requirements.txt"
if [ -f "$REQ_FILE" ]; then
  echo "� Installing Python requirements from $REQ_FILE..."
  pip3 install --break-system-packages -r "$REQ_FILE"
  echo "✅ Python requirements installed."
else
  echo "⚠️  $REQ_FILE not found. Skipping Python requirements install."
fi

# --- Step 3: Uninstall Previous Package ---
echo "\n🔄 STEP 3: Uninstall Previous $PKG_NAME Package\n========================================"
if pip3 show $PKG_NAME > /dev/null 2>&1; then
  echo "🗑️  Removing old $PKG_NAME..."
  pip3 uninstall --break-system-packages -y $PKG_NAME
else
  echo "✅ No previous installation of $PKG_NAME found."
fi

# --- Step 4: Install Package ---
echo "\n🛠️  STEP 4: Install $PKG_NAME Package\n========================================"
pip3 install --break-system-packages -e .
echo "✅ $PKG_NAME installed."


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