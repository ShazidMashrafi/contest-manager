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

echo "[1/6] Installing system packages..."
apt-get update
apt-get install -y $SYSTEM_PACKAGES python3-setuptools

echo "[2/6] Upgrading setuptools..."
pip3 install --break-system-packages --upgrade setuptools


echo "[3/6] Checking for previous installation of contest-manager..."
if pip3 show contest-manager > /dev/null 2>&1; then
  echo "Previous installation of contest-manager found. Uninstalling..."
  pip3 uninstall --break-system-packages -y contest-manager
else
  echo "No previous installation of contest-manager found."
fi

echo "[4/6] Installing Python package in development (editable) mode (with PEP 668 workaround)..."
PIP_BREAK_SYSTEM_PACKAGES=1 pip3 install --break-system-packages -e .

echo "[5/6] Installing Playwright browsers and dependencies (system-wide)..."
$PLAYWRIGHT_DEPS_CMD
$PLAYWRIGHT_INSTALL_CMD

echo "[6/6] Setup complete!"
echo "You can now use contest-manager CLI commands."
