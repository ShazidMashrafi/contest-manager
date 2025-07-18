import tempfile
import requests
import subprocess
from pathlib import Path

def install_apt_softwares(apt_file, verbose=False):
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

def install_deb_softwares(deb_file, verbose=False):
    print("\n================= [DEB INSTALL] ==================")
    """Download and install .deb packages listed in deb_file (one URL per line)."""
    if not Path(deb_file).exists():
        print(f"[deb] Package list not found: {deb_file}")
        return
    installed = []
    failed = []
    with open(deb_file) as f:
        for line in f:
            url = line.strip()
            if not url or url.startswith('#'):
                continue
            try:
                print(f"[deb] 🛠️ Downloading: {url}")
                with tempfile.NamedTemporaryFile(suffix='.deb', delete=False) as tmp:
                    response = requests.get(url, stream=True)
                    if response.status_code == 200:
                        for chunk in response.iter_content(chunk_size=8192):
                            tmp.write(chunk)
                        tmp_path = tmp.name
                        print(f"[deb] 🛠️ Installing: {tmp_path}")
                        subprocess.run(['apt', 'install', '-y', tmp_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        print(f"[deb] ✅ Installed: {url}")
                        installed.append(url)
                    else:
                        print(f"[deb] ❌ Failed to download: {url} (HTTP {response.status_code})")
                        failed.append(url)
            except Exception as e:
                print(f"[deb] ❌ Failed: {url} ({e})")
                failed.append(url)
    print(f"[deb] Install summary: ✅ {len(installed)} succeeded, ❌ {len(failed)} failed.")
    if failed:
        print("[deb] ❌ Failed packages:")
        for url in failed:
            print(f"  - {url}")

def install_snap_softwares(snap_file, verbose=False):
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
                subprocess.run(cmd, check=True)
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

def install_flatpak_softwares(flatpak_file, verbose=False):
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

def install_all_softwares(verbose=False):
    config_dir = Path(__file__).parent.parent.parent / 'config'
    apt_file = config_dir / 'apt.txt'
    deb_file = config_dir / 'deb.txt'
    snap_file = config_dir / 'snap.txt'
    flatpak_file = config_dir / 'flatpak.txt'
    install_apt_softwares(apt_file, verbose=verbose)
    install_deb_softwares(deb_file, verbose=verbose)
    install_snap_softwares(snap_file, verbose=verbose)
    install_flatpak_softwares(flatpak_file, verbose=verbose)