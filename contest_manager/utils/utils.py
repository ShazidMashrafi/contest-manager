import os
import sys
import shutil
import subprocess

def run_command(cmd, shell=False, check=True, capture_output=False):
    """Run a command and handle errors."""
    try:
        if shell:
            result = subprocess.run(cmd, shell=True, check=check, 
                                  capture_output=capture_output, text=True)
        else:
            result = subprocess.run(cmd, check=check, capture_output=capture_output, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e.cmd}")
        if capture_output:
            print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def check_root():
    if os.geteuid() != 0:
        print("❌ Error: This command must be run as root")
        sys.exit(1)

def disable_system_updates():
    print("→ Disabling automatic system updates...")
    services = ["apt-daily.service", "apt-daily-upgrade.service"]
    for service in services:
        run_command(f"systemctl stop {service}", shell=True, check=False)
        run_command(f"systemctl disable {service}", shell=True, check=False)
    print("✅ Automatic system updates disabled.")

def cleanup_system():
    print("→ Cleaning up system...")
    run_command("apt autoremove -y", shell=True)
    run_command("apt autoclean", shell=True)
    print("✅ System cleanup completed.")
    

def fix_vscode_keyring(user):
    print("→ Fixing VS Code keyring issues...")
    run_command("apt install -y libpam-gnome-keyring", shell=True)
    auth_file = "/etc/pam.d/common-auth"
    session_file = "/etc/pam.d/common-session"
    with open(auth_file, 'r') as f:
        content = f.read()
    if "pam_gnome_keyring.so" not in content:
        with open(auth_file, 'a') as f:
            f.write("auth optional pam_gnome_keyring.so\n")
    with open(session_file, 'r') as f:
        content = f.read()
    if "pam_gnome_keyring.so auto_start" not in content:
        with open(session_file, 'a') as f:
            f.write("session optional pam_gnome_keyring.so auto_start\n")
    keyring_dir = f"/home/{user}/.local/share/keyrings"
    if os.path.exists(keyring_dir):
        shutil.rmtree(keyring_dir)
    print("✅ VS Code keyring issues fixed.")
    
def fix_codeblocks_permissions(user):
    print("→ Fixing CodeBlocks permissions...")
    run_command("apt install -y acl", shell=True)
    home_dir = f"/home/{user}"
    cb_projects = f"{home_dir}/cb_projects"
    cb_bin = f"{cb_projects}/bin"
    run_command(f"sudo -u {user} mkdir -p {cb_projects}/bin/Debug", shell=True)
    run_command(f"sudo -u {user} mkdir -p {cb_projects}/bin/Release", shell=True)
    run_command(f"chown -R {user}:{user} {home_dir}", shell=True)
    run_command(f"chmod -R u+rwX {home_dir}", shell=True)
    run_command(f"setfacl -R -d -m u::rwx,g::rx,o::rx {cb_bin}", shell=True)
    run_command(f"setfacl -R -m u::rwx,g::rx,o::rx {cb_bin}", shell=True)
    run_command(f"find {cb_bin} -type f -exec chmod +x {{}} \\;", shell=True, check=False)
    print("✅ CodeBlocks permissions fixed.")


def add_apt_repos(verbose=False):
    cmds = [
        ['add-apt-repository', '-y', 'universe'],
        ['add-apt-repository', '-y', 'multiverse'],
        ['apt-get', 'update']
    ]
    for cmd in cmds:
        try:
            if verbose:
                print(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
        except Exception as e:
            print(f"Error running {' '.join(cmd)}: {e}")
            raise
