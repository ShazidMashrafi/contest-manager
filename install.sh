#!/bin/bash
# Contest Environment Manager Installer (Minimal)
set -e

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root: sudo $0"
  exit 1
fi

echo "[1/2] Uninstalling previous contest-manager package (if any)..."
if pip3 show contest-manager > /dev/null 2>&1; then
  pip3 uninstall -y contest-manager
else
  echo "No previous installation of contest-manager found."
fi

echo "[2/2] Installing contest-manager dependencies..."
pip3 install --break-system-packages -r requirements.txt
echo "Installing contest-manager in editable mode..."
pip3 install --break-system-packages -e .

echo "Setup complete! You can now use contest-manager CLI commands."
