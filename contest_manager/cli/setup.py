#!/usr/bin/env python3
"""
Contest Environment Setup CLI
"""

import sys
from pathlib import Path
from contest_manager.utils.utils import *
from contest_manager.utils.user_manager import *
from contest_manager.utils.package_manager_setup import *
from contest_manager.utils.package_installer import *
from contest_manager.utils.vscode_extensions_handler import *



CONFIG_DIR = Path(__file__).parent.parent.parent / 'config'
USERS_TXT = CONFIG_DIR / 'users.txt'
APT_TXT = CONFIG_DIR / 'apt.txt'
SNAP_TXT = CONFIG_DIR / 'snap.txt'
FLATPAK_TXT = CONFIG_DIR / 'flatpak.txt'
VSCODE_EXTENSIONS = CONFIG_DIR / 'vscode-extensions.txt'



def main():
    check_root()

    print("\n🧑  STEP 1: User Account\n" + ("="*40))
    setup_users(USERS_TXT)

    print("\n🗂️  STEP 2: System Repositories & Core Tools\n" + ("="*40))
    setup_package_sources(APT_TXT)

    print("\n💻 STEP 3: Applications\n" + ("="*40))
    install_apt_packages(APT_TXT)
    install_snap_packages(SNAP_TXT)
    install_flatpak_packages(FLATPAK_TXT)

    print("\n🧩 STEP 4: VS Code Extensions\n" + ("="*40))
    install_vscode_extensions(VSCODE_EXTENSIONS)

    print("\n🚫 STEP 5: Disable System Updates\n" + ("="*40))
    disable_system_updates()

    print("\n🧹 STEP 6: Cleanup\n" + ("="*40))
    cleanup_system()

    print("\n🗄️  STEP 7: Backing up home\n" + ("="*40))
    user_pairs = extract_user_password_pairs(USERS_TXT)
    for username, _ in user_pairs:
        create_user_backup(username)

    print("\n🎉✅ Setup complete!")
    sys.exit(0)

if __name__ == "__main__":
    main()