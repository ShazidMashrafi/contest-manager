#!/bin/bash
# Contest Environment Manager Installer
# Installs all system dependencies and the Python package in editable mode
set -e

REQ_DIR="$(dirname "$0")/requirements"
PY_REQ_FILE="$REQ_DIR/requirements.txt"
SYS_REQ_FILE="$REQ_DIR/system-requirements.txt"

# System dependencies
SYSTEM_PACKAGES=$(grep -v '^#' "$SYS_REQ_FILE" | grep -v '^$' | tr '\n' ' ')

# Playwright browser dependencies
PLAYWRIGHT_DEPS_CMD="python3 -m playwright install-deps"
PLAYWRIGHT_INSTALL_CMD="python3 -m playwright install"

# Install system packages
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root: sudo $0"
  exit 1
fi

echo "[1/5] Installing system packages..."
apt-get update
apt-get install -y $SYSTEM_PACKAGES

echo "[2/5] Uninstalling any existing package (with PEP 668 workaround)..."
pip3 uninstall --break-system-packages -y contest-environment-manager || true

echo "[3/5] Installing Python package in development (editable) mode (with PEP 668 workaround)..."
pip3 install --break-system-packages -e .

echo "[4/5] Installing Playwright browsers and dependencies (system-wide)..."
$PLAYWRIGHT_DEPS_CMD
$PLAYWRIGHT_INSTALL_CMD

echo "[5/5] Setup complete!"
echo "You can now use contest-manager CLI commands."
