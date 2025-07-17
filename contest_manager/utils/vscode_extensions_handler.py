import subprocess
from pathlib import Path

def install_vscode_extensions(ext_file, user=None, verbose=False):
    """Install VS Code extensions from a file."""
    print("\n================ [VSCODE EXTENSIONS] ================")
    if not Path(ext_file).exists():
        print(f"[vscode] ❌ Extensions file not found: {ext_file}")
        return
    extensions = get_extensions_from_file(ext_file)
    installed = []
    failed = []
    for ext in extensions:
        if is_extension_installed(ext):
            print(f"[vscode] ⏩ Already installed: {ext}")
            continue
        if install_extension(ext):
            installed.append(ext)
        else:
            failed.append(ext)
    print(f"[vscode] Install summary: ✅ {len(installed)} succeeded, ❌ {len(failed)} failed.")
    if failed:
        print("[vscode] ❌ Failed extensions:")
        for ext in failed:
            print(f"  - {ext}")

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
    cmd = ['code', '--install-extension', ext]
    if user:
        cmd = ['sudo', '-u', user] + cmd
    try:
        print(f"[vscode] 🛠️ Installing: {ext}")
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"[vscode] ✅ Installed: {ext}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[vscode] ❌ Failed: {ext} ({e})")
        return False
