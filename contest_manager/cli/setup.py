#!/usr/bin/env python3
"""
Contest Environment Setup CLI
"""

import sys
import argparse
import subprocess
from pathlib import Path
from ..core.manager import ContestManager
from ..utils.common import check_root, get_project_root
from ..utils.user_manager import delete_user_account, create_contest_user
from ..utils.software_installer import install_vscode_extensions
from ..utils.system_utils import (
    cleanup_system, clean_temporary_files
)
from ..utils.setup_utils import add_apt_repos, install_snap_flatpak, fix_permissions_and_keyring, create_backup

INSTALL_TXT = Path(__file__).parent.parent.parent / 'install.txt'
VSCODE_EXTENSIONS = Path(__file__).parent.parent.parent / 'vscode-extensions.txt'


def create_parser():
    """Create the setup argument parser."""
    parser = argparse.ArgumentParser(
        description="Set up lab PC with all required software and user account",
        prog="contest-setup"
    )
    
    parser.add_argument(
        'user',
        nargs='?',
        default='participant',
        help='Username to set up (default: participant)'
    )
    
    parser.add_argument(
        '--config-dir',
        type=str,
        help='Configuration directory path (default: project root)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser


def install_packages_from_file(file_path, verbose=False):
    """Install packages listed in a file using apt-get, fallback to snap, then flatpak."""
    import shutil
    if not file_path.exists():
        print(f"Install file not found: {file_path}")
        sys.exit(1)
    with open(file_path) as f:
        pkgs = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    if not pkgs:
        print("No packages to install.")
        return
    not_found = []
    for pkg in pkgs:
        # Try apt install
        cmd = ['apt-get', 'install', '-y', pkg]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"[apt] Installed: {pkg}")
            continue
        except subprocess.CalledProcessError:
            print(f"[apt] Not found: {pkg}")
        # Try snap install
        if shutil.which('snap'):
            try:
                subprocess.run(['snap', 'install', pkg], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"[snap] Installed: {pkg}")
                continue
            except subprocess.CalledProcessError:
                print(f"[snap] Not found: {pkg}")
        # Try flatpak install
        if shutil.which('flatpak'):
            try:
                subprocess.run(['flatpak', 'install', '-y', pkg], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"[flatpak] Installed: {pkg}")
                continue
            except subprocess.CalledProcessError:
                print(f"[flatpak] Not found: {pkg}")
        not_found.append(pkg)
    if not_found:
        print("Could not install the following packages via apt, snap, or flatpak:")
        for pkg in not_found:
            print(f"  - {pkg}")


def install_vscode_exts(user, verbose=False):
    """Install VS Code extensions from file for a user."""
    if not VSCODE_EXTENSIONS.exists():
        print(f"VS Code extensions file not found: {VSCODE_EXTENSIONS}")
        return
    if verbose:
        print(f"Installing VS Code extensions for {user} from {VSCODE_EXTENSIONS}")
    install_vscode_extensions(user)


def disable_auto_updates(verbose=False):
    from ..utils.system_utils import disable_system_updates
    disable_system_updates()


def cleanup(verbose=False):
    cleanup_system()
    # Optionally clean temp for all users
    # clean_temporary_files(user)


def main():
    """Main setup CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    check_root()
    
    # 1. Delete and recreate user
    delete_user_account(args.user)
    if not create_contest_user(args.user):
        print(f"Failed to create contest user: {args.user}")
        sys.exit(1)

    # 2. Add repos, update, install snap/flatpak
    add_apt_repos(verbose=args.verbose)
    install_snap_flatpak(verbose=args.verbose)

    # 3. Install packages from install.txt
    install_packages_from_file(INSTALL_TXT, verbose=args.verbose)

    # 4. Install VS Code extensions
    install_vscode_exts(args.user, verbose=args.verbose)

    # 5. Fix permissions and keyring
    fix_permissions_and_keyring(args.user, verbose=args.verbose)

    # 6. Disable auto updates
    disable_auto_updates(verbose=args.verbose)

    # 7. Cleanup
    cleanup(verbose=args.verbose)

    # 8. Backup
    create_backup(args.user, verbose=args.verbose)

    print("Setup complete!")
    sys.exit(0)


if __name__ == "__main__":
    main()
