import subprocess
from pathlib import Path

def install_apt_packages(apt_file, verbose=False):
    print("\n==================== [APT INSTALL] ====================")
    """Install apt packages listed in apt_file."""
    if not Path(apt_file).exists():
        print(f"[apt] Package list not found: {apt_file}")
        return
    pkgs = []
    ppas = []
    with open(apt_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '(' in line and 'ppa:' in line:
                pkg = line.split('(')[0].strip()
                ppa = line.split('ppa:')[1].strip(') ')
                ppas.append(ppa)
                pkgs.append(pkg)
            else:
                pkgs.append(line)
    # Add PPAs (handled in setup.py now)
    # Install packages
    installed = []
    failed = []
    for pkg in pkgs:
        try:
            print(f"[apt] 🛠️ Installing: {pkg}")
            subprocess.run(['apt-get', 'install', '-y', pkg], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"[apt] ✅ Installed: {pkg}")
            installed.append(pkg)
        except subprocess.CalledProcessError as e:
            print(f"[apt] ❌ Failed: {pkg} ({e})")
            failed.append(pkg)
    print(f"[apt] Install summary: ✅ {len(installed)} succeeded, ❌ {len(failed)} failed.")
    if failed:
        print("[apt] ❌ Failed packages:")
        for pkg in failed:
            print(f"  - {pkg}")

def install_snap_packages(snap_file, verbose=False):
    print("\n==================== [SNAP INSTALL] ===================")
    """Install snap packages listed in snap_file."""
    if not Path(snap_file).exists():
        print(f"[snap] Package list not found: {snap_file}")
        return
    installed = []
    failed = []
    with open(snap_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            cmd = ['snap', 'install'] + line.split()
            pkg_name = ' '.join(cmd[2:])
            try:
                print(f"[snap] 🛠️ Installing: {pkg_name}")
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(f"[snap] ✅ Installed: {pkg_name}")
                installed.append(pkg_name)
            except subprocess.CalledProcessError as e:
                print(f"[snap] ❌ Failed: {pkg_name} ({e})")
                failed.append(pkg_name)
    print(f"[snap] Install summary: ✅ {len(installed)} succeeded, ❌ {len(failed)} failed.")
    if failed:
        print("[snap] ❌ Failed packages:")
        for pkg in failed:
            print(f"  - {pkg}")

def install_flatpak_packages(flatpak_file, verbose=False):
    print("\n================= [FLATPAK INSTALL] ==================")
    """Install flatpak packages listed in flatpak_file."""
    if not Path(flatpak_file).exists():
        print(f"[flatpak] Package list not found: {flatpak_file}")
        return
    installed = []
    failed = []
    with open(flatpak_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            cmd = ['flatpak', 'install', '-y'] + line.split()
            pkg_name = ' '.join(cmd[3:])
            try:
                print(f"[flatpak] 🛠️ Installing: {pkg_name}")
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(f"[flatpak] ✅ Installed: {pkg_name}")
                installed.append(pkg_name)
            except subprocess.CalledProcessError as e:
                print(f"[flatpak] ❌ Failed: {pkg_name} ({e})")
                failed.append(pkg_name)
    print(f"[flatpak] Install summary: ✅ {len(installed)} succeeded, ❌ {len(failed)} failed.")
    if failed:
        print("[flatpak] ❌ Failed packages:")
        for pkg in failed:
            print(f"  - {pkg}")
