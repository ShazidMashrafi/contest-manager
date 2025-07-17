#!/usr/bin/env python3
"""
Contest Environment Setup CLI
"""
import sys
import argparse
from pathlib import Path
from ..utils.utils import *
from ..utils.user_manager import create_contest_user
from ..utils.package_manager_setup import setup_package_sources
from ..utils.package_installer import *
from ..utils.vscode_extensions_handler import *


# Use config directory for user-editable lists
CONFIG_DIR = Path(__file__).parent.parent.parent / 'config'
APT_TXT = CONFIG_DIR / 'apt.txt'
SNAP_TXT = CONFIG_DIR / 'snap.txt'
FLATPAK_TXT = CONFIG_DIR / 'flatpak.txt'
VSCODE_EXTENSIONS = CONFIG_DIR / 'vscode-extensions.txt'

def create_parser():
    """Create the setup argument parser."""
    parser = argparse.ArgumentParser(
        description="Set up lab PC with all required software and user account",
        prog="contest-setup"
    )
    parser.add_argument(
        'user', nargs='?', default='participant', help='Username to set up (default: participant)'
    )
    parser.add_argument(
        '--config-dir', type=str, help='Configuration directory path (default: project root)'
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true', help='Enable verbose output'
    )
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    check_root()

    print("\n🧑  STEP 1: User Account\n" + ("="*40))
    create_contest_user(args.user)

    print("\n🗂️  STEP 2: System Repositories & Core Tools\n" + ("="*40))
    setup_package_sources(APT_TXT)

    print("\n💻 STEP 3: Applications\n" + ("="*40))
    install_apt_packages(APT_TXT, verbose=args.verbose)
    install_snap_packages(SNAP_TXT, verbose=args.verbose)
    install_flatpak_packages(FLATPAK_TXT, verbose=args.verbose)

    print("\n🧩 STEP 4: VS Code Extensions\n" + ("="*40))
    install_vscode_extensions(VSCODE_EXTENSIONS, user=args.user, verbose=args.verbose)

    print("\n🚫 STEP 5: Disable System Updates\n" + ("="*40))
    disable_system_updates()

    print("\n🧹 STEP 6: Cleanup\n" + ("="*40))
    cleanup_system()

    print("\n🗄️  STEP 7: Backing up home\n" + ("="*40))
    create_home_backup(args.user, verbose=args.verbose)

    print("\n🎉✅ Setup complete!")
    sys.exit(0)

if __name__ == "__main__":
    main()