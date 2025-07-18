import os
import subprocess
from pathlib import Path
from shutil import which
import pwd

from contest_manager.utils.user_manager import extract_user_password_pairs

CONFIG_DIR = Path(__file__).parent.parent.parent / 'config'
USERS_TXT = CONFIG_DIR / 'users.txt'

def get_extensions_from_file(ext_file):
    """Read extension list from file, ignoring comments and blanks."""
    extensions = []
    with open(ext_file) as f:
        for line in f:
            ext = line.strip()
            if ext and not ext.startswith('#'):
                extensions.append(ext)
    return extensions

def is_extension_installed(ext, user=None):
    """Check if a VS Code extension is already installed for the user."""
    cmd = ['code', '--list-extensions']
    if user:
        cmd = ['sudo', '-u', user] + cmd
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        installed_exts = result.stdout.decode().splitlines()
        return ext in installed_exts
    except Exception as e:
        print(f"[vscode] ⚠️ Could not check installed extensions for {ext}: {e}")
        return False


def install_extension(ext, user=None):
    """Install a single VS Code extension for the user."""
    # Set HOME for the user to ensure correct extension install location
    env = None
    if user:
        try:
            pw_record = pwd.getpwnam(user)
            user_home = pw_record.pw_dir
            env = os.environ.copy()
            env['HOME'] = user_home
            cmd = ['sudo', '-u', user, 'env', f'HOME={user_home}', 'code', '--install-extension', ext]
        except Exception as e:
            print(f"[vscode] ❌ Could not get home for user {user}: {e}")
            return False
    else:
        cmd = ['code', '--install-extension', ext]
    try:
        print(f"[vscode] 🛠️ Installing: {ext}")
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        print(f"[vscode] ✅ Installed: {ext}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[vscode] ❌ Failed: {ext} ({e})")
        return False

def install_vscode_extensions(ext_file, user=None, verbose=False):
    """Install VS Code extensions from a file."""
    print("\n================ [VSCODE EXTENSIONS] ================")
    code_path = which('code')
    if not code_path:
        print("[vscode] ❌ VS Code ('code') is not installed system-wide. Skipping all extension installs.")
        return
    if not Path(ext_file).exists():
        print(f"[vscode] ❌ Extensions file not found: {ext_file}")
        return
    extensions = get_extensions_from_file(ext_file)
    user_pairs = extract_user_password_pairs(USERS_TXT)
    usernames = [u for u, _ in user_pairs]
    total_installed = 0
    total_failed = 0
    failed_exts = set()
    for username in usernames:
        print(f"\n[vscode] Installing extensions for user: {username}")
        # Pre-create VS Code config folders for the user
        try:
            pw_record = pwd.getpwnam(username)
            user_home = pw_record.pw_dir
            vscode_dir = Path(user_home) / '.vscode'
            config_code_dir = Path(user_home) / '.config' / 'Code'
            vscode_dir.mkdir(parents=True, exist_ok=True)
            config_code_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"[vscode] ⚠️ Could not create VS Code config folders for {username}: {e}")
        # Initialize VS Code profile for the user
        try:
            env = os.environ.copy()
            env['HOME'] = user_home
            cmd = ['sudo', '-u', username, 'env', f'HOME={user_home}', 'code', '--list-extensions']
            subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        except Exception as e:
            print(f"[vscode] ⚠️ Could not initialize VS Code profile for {username}: {e}")
        for ext in extensions:
            if is_extension_installed(ext, user=username):
                print(f"[vscode] ⏩ Already installed for {username}: {ext}")
                continue
            if install_extension(ext, user=username):
                total_installed += 1
            else:
                total_failed += 1
                failed_exts.add(ext)
    print(f"[vscode] Install summary: ✅ {total_installed} succeeded, ❌ {total_failed} failed.")
    if failed_exts:
        print("[vscode] ❌ Failed extensions:")
        for ext in failed_exts:
            print(f"  - {ext}")