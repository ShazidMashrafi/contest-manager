import subprocess
import shutil
import time
from pathlib import Path

def add_apt_repos(verbose=False):
    cmds = [
        ['add-apt-repository', '-y', 'universe'],
        ['add-apt-repository', '-y', 'multiverse'],
    ]
    for cmd in cmds:
        try:
            if verbose:
                print(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
        except Exception as e:
            print(f"Error running {' '.join(cmd)}: {e}")
            raise

def parse_ppas_from_file(apt_txt):
    """Parse PPAs from apt.txt config file."""
    ppas = []
    if Path(apt_txt).exists():
        with open(apt_txt) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '(' in line and 'ppa:' in line:
                    ppa = line.split('ppa:')[1].strip(') ')
                    ppas.append(ppa)
    return ppas

def add_ppas(ppas):
    """Add PPAs to the system."""
    for ppa in ppas:
        try:
            print(f"Adding PPA: {ppa}")
            subprocess.run(['add-apt-repository', '-y', f'ppa:{ppa}'], check=True)
        except Exception as e:
            print(f"Failed to add PPA: {ppa}: {e}")

def update_apt_repos():
    """Update apt repositories."""
    print("🔄 Updating apt repositories...")
    subprocess.run(['apt-get', 'update'], check=True)

def ensure_snap():
    """Ensure snapd is installed and running."""
    if shutil.which('snap') is None:
        print("📦 Installing snapd...")
        subprocess.run(['apt-get', 'install', '-y', 'snapd'], check=True)
    try:
        subprocess.run(['systemctl', 'start', 'snapd'], check=True)
    except Exception:
        pass
    time.sleep(2)

def ensure_flatpak():
    """Ensure flatpak is installed and flathub remote is added."""
    if shutil.which('flatpak') is None:
        print("📦 Installing flatpak...")
        subprocess.run(['apt-get', 'install', '-y', 'flatpak'], check=True)
    try:
        remotes = subprocess.check_output(['flatpak', 'remotes'], text=True)
        if 'flathub' not in remotes:
            print("Adding Flathub remote to Flatpak...")
            subprocess.run(['flatpak', 'remote-add', '--if-not-exists', 'flathub', 'https://flathub.org/repo/flathub.flatpakrepo'], check=True)
    except Exception:
        pass

def setup_package_sources(apt_txt):
    add_apt_repos()
    ppas = parse_ppas_from_file(apt_txt)
    add_ppas(ppas)
    update_apt_repos()
    ensure_snap()
    ensure_flatpak()