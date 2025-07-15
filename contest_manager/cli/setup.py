#!/usr/bin/env python3
"""
Contest Environment Setup CLI
"""

import sys
import argparse
import subprocess
import time
import shutil
from pathlib import Path
from ..utils.common import check_root, get_project_root
from ..utils.user_manager import create_contest_user
from ..utils.software_installer import install_vscode_extensions
from ..utils.system_utils import cleanup_system, clean_temporary_files
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
        'user', nargs='?', default='participant', help='Username to set up (default: participant)'
    )
    parser.add_argument(
        '--config-dir', type=str, help='Configuration directory path (default: project root)'
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true', help='Enable verbose output'
    )
    return parser




def parse_install_lines(file_path):
    with open(file_path) as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    pkg_ppas = []
    normal_pkgs = []
    for line in lines:
        if '(' in line and line.endswith(')') and 'ppa:' in line:
            pkg = line.split('(')[0].strip()
            ppa = line.split('(')[1].strip(') ').strip()
            pkg_ppas.append((pkg, ppa))
        else:
            normal_pkgs.append(line)
    return pkg_ppas, normal_pkgs


def ensure_snap_flatpak():
    # Snap
    if shutil.which('snap') is None:
        print("Installing snapd...")
        subprocess.run(['apt-get', 'install', '-y', 'snapd'], check=True)
    try:
        subprocess.run(['systemctl', 'start', 'snapd'], check=True)
    except Exception:
        pass
    time.sleep(2)
    # Flatpak
    if shutil.which('flatpak') is None:
        print("Installing flatpak...")
        subprocess.run(['apt-get', 'install', '-y', 'flatpak'], check=True)
    try:
        remotes = subprocess.check_output(['flatpak', 'remotes'], text=True)
        if 'flathub' not in remotes:
            print("Adding Flathub remote to Flatpak...")
            subprocess.run(['flatpak', 'remote-add', '--if-not-exists', 'flathub', 'https://flathub.org/repo/flathub.flatpakrepo'], check=True)
    except Exception:
        pass


def add_ppas(pkg_ppas):
    for pkg, ppa in pkg_ppas:
        print(f"Adding PPA: {ppa} for package: {pkg}")
        try:
            subprocess.run(['add-apt-repository', '-y', ppa], check=True)
        except subprocess.CalledProcessError:
            print(f"Failed to add PPA: {ppa}")
    if pkg_ppas:
        subprocess.run(['apt-get', 'update'], check=True)


def try_install_package(pkg):
    # Try apt
    cmd = ['apt-get', 'install', '-y', pkg]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[apt] Installed: {pkg}")
        return True
    except subprocess.CalledProcessError:
        print(f"[apt] Not found: {pkg}")
    # Try snap
    if shutil.which('snap'):
        try:
            subprocess.run(['snap', 'install', pkg], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"[snap] Installed: {pkg}")
            return True
        except subprocess.CalledProcessError:
            print(f"[snap] Not found: {pkg}")
    # Try flatpak
    if shutil.which('flatpak'):
        try:
            subprocess.run(['flatpak', 'install', '-y', pkg], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"[flatpak] Installed: {pkg}")
            return True
        except subprocess.CalledProcessError:
            print(f"[flatpak] Not found: {pkg}")
    return False


def install_packages_from_file(file_path, verbose=False):
    """Install packages and add PPAs as listed in a file."""
    if not file_path.exists():
        print(f"Install file not found: {file_path}")
        sys.exit(1)
    pkg_ppas, normal_pkgs = parse_install_lines(file_path)
    ensure_snap_flatpak()
    add_ppas(pkg_ppas)
    not_found = []
    # Install PPA packages first
    for pkg, _ in pkg_ppas:
        if not try_install_package(pkg):
            not_found.append(pkg)
    # Install normal packages
    for pkg in normal_pkgs:
        if not try_install_package(pkg):
            not_found.append(pkg)
    if not_found:
        print("Could not install the following packages via apt, snap, or flatpak:")
        for pkg in not_found:
            print(f"  - {pkg}")


def main():
    parser = create_parser()
    args = parser.parse_args()
    check_root()
    # 1. Create (and if exists, delete and recreate) user
    if not create_contest_user(args.user):
        print(f"Failed to create contest user: {args.user}")
        sys.exit(1)
    # 2. Add repos, update, install snap/flatpak
    add_apt_repos(verbose=args.verbose)
    install_snap_flatpak(verbose=args.verbose)
    # 3. Install packages from install.txt
    install_packages_from_file(INSTALL_TXT, verbose=args.verbose)
    # 4. Install VS Code extensions
    if VSCODE_EXTENSIONS.exists():
        install_vscode_extensions(args.user)
    # 5. Fix permissions and keyring
    fix_permissions_and_keyring(args.user, verbose=args.verbose)
    # 6. Disable auto updates
    from ..utils.system_utils import disable_system_updates
    disable_system_updates()
    # 7. Cleanup
    cleanup_system()
    # 8. Backup
    create_backup(args.user, verbose=args.verbose)
    print("Setup complete!")
    sys.exit(0)

if __name__ == "__main__":
    main()