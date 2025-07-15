import subprocess
from pathlib import Path

def install_vscode_extensions(ext_file, user=None, verbose=False):
    """Install VS Code extensions from a file."""
    if not Path(ext_file).exists():
        print(f"[vscode] Extensions file not found: {ext_file}")
        return
    installed = []
    failed = []
    with open(ext_file) as f:
        for line in f:
            ext = line.strip()
            if not ext or ext.startswith('#'):
                continue
            cmd = ['code', '--install-extension', ext]
            if user:
                cmd = ['sudo', '-u', user] + cmd
            try:
                if verbose:
                    print(f"[vscode] Installing extension: {ext}")
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(f"[vscode] Installed: {ext}")
                installed.append(ext)
            except subprocess.CalledProcessError as e:
                print(f"[vscode] Failed: {ext} ({e})")
                failed.append(ext)
    print(f"[vscode] Install summary: {len(installed)} succeeded, {len(failed)} failed.")
    if failed:
        print("[vscode] Failed extensions:")
        for ext in failed:
            print(f"  - {ext}")
