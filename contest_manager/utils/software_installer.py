#!/usr/bin/env python3
"""
Software installation utilities for contest environment.
"""

from .common import run_command, command_exists, package_installed, install_packages


def install_vscode_extensions(user):
    """Install VS Code extensions for a user from vscode-extensions.txt."""
    import pathlib
    extensions_file = pathlib.Path(__file__).parent.parent.parent / 'vscode-extensions.txt'
    try:
        if not extensions_file.exists():
            print(f"VS Code extensions file not found: {extensions_file}")
            return False
        with open(extensions_file) as f:
            extensions = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        all_ok = True
        user_data_dir = f"/home/{user}/.config/Code"
        for ext in extensions:
            # Check if extension is already installed (more robust)
            check_cmd = f"sudo -u {user} code --user-data-dir={user_data_dir} --list-extensions | grep -Fxq '{ext}'"
            check_result = run_command(check_cmd, shell=True, check=False, capture_output=True)
            if check_result.returncode == 0:
                print(f"✅ Extension {ext} is already installed.")
                continue
            print(f"→ Installing extension: {ext}")
            result = run_command(f"timeout 60s sudo -u {user} code --user-data-dir={user_data_dir} --install-extension {ext} --force", shell=True, check=False, capture_output=True)
            if result.returncode == 0:
                print(f"✅ Extension {ext} installed successfully.")
            else:
                print(f"⚠️ Failed to install {ext} (may be due to network issues)")
                all_ok = False
        return all_ok
    except Exception as e:
        print(f"❌ Failed to install VS Code extensions: {e}")
        return False


def verify_essential_software() -> bool:
    """Verify that all packages in install.txt are installed."""
    import pathlib
    from .common import package_installed
    install_file = pathlib.Path(__file__).parent.parent.parent / 'install.txt'
    print("→ Verifying essential software from install.txt...")
    if not install_file.exists():
        print(f"install.txt not found: {install_file}")
        return False
    with open(install_file) as f:
        packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    missing_packages = []
    for package in packages:
        if not package_installed(package):
            missing_packages.append(package)
    if missing_packages:
        print(f"❌ Missing essential software: {', '.join(missing_packages)}")
        return False
    else:
        print("✅ All essential software from install.txt is installed")
        return True
