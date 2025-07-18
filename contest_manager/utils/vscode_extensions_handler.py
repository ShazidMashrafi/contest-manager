
import os
import shutil
import subprocess
from pathlib import Path

def find_vscode_cli():
    """Find VS Code CLI executable (code or code-insiders)."""
    for exe in ["code", "code-insiders"]:
        path = shutil.which(exe)
        if path:
            return path
    # Try common install locations
    for path in ["/usr/bin/code", "/usr/local/bin/code", "/opt/code/bin/code", "/usr/share/code/bin/code"]:
        if Path(path).exists():
            return path
    return None

def is_vscode_installed():
    """Return True if VS Code CLI is available."""
    return find_vscode_cli() is not None

def get_installed_extensions(code_path):
    """Return a set of installed extension IDs."""
    try:
        result = subprocess.run([code_path, "--list-extensions"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return set(result.stdout.strip().splitlines())
    except Exception:
        return set()

def read_extensions(ext_file):
    """Read extension IDs from file."""
    ext_ids = []
    if Path(ext_file).exists():
        with open(ext_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    ext_ids.append(line)
    return ext_ids

def install_extension(code_path, ext_id):
    """Install a single extension."""
    try:
        cmd = [code_path, "--install-extension", ext_id]
        # If running as root, add --no-sandbox and --user-data-dir
        if os.geteuid() == 0:
            user_data_dir = "/tmp/vscode-root"
            os.makedirs(user_data_dir, exist_ok=True)
            cmd += ["--no-sandbox", f"--user-data-dir={user_data_dir}"]
        subprocess.run(cmd, check=True)
        print(f"[vscode] ✅ Installed extension: {ext_id}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[vscode] ❌ Failed to install {ext_id}: {e}")
        return False

def install_vscode_extensions(ext_file):
    """Main entry: install extensions from ext_file if VS Code is installed."""
    code_path = find_vscode_cli()
    if not code_path:
        print("[vscode] VS Code CLI not found. Skipping extension install.")
        return
    print(f"[vscode] Found VS Code CLI: {code_path}")
    ext_ids = read_extensions(ext_file)
    installed_exts = get_installed_extensions(code_path)
    for ext_id in ext_ids:
        if ext_id in installed_exts:
            print(f"[vscode] Already installed: {ext_id}")
        else:
            install_extension(code_path, ext_id)
