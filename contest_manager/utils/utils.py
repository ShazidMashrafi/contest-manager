import os
import shutil
import subprocess
from pathlib import Path
from .common import run_command, print_status, print_error, print_warning

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

def clean_temporary_files(user: str) -> bool:
    print("→ Cleaning temporary files...")
    try:
        user_home = f"/home/{user}"
        temp_patterns = ["*.tmp", "*.bak", "*.*~", "*.swp", "*.swo"]
        for pattern in temp_patterns:
            cmd = f"find {user_home} -name '{pattern}' -type f -delete"
            run_command(cmd, shell=True, check=False)
        cache_dirs = [
            f"{user_home}/.cache",
            f"{user_home}/.local/share/Trash",
            f"{user_home}/.config/Code/logs",
            f"{user_home}/.config/Code/CachedData"
        ]
        for cache_dir in cache_dirs:
            if os.path.exists(cache_dir):
                print(f"→ Cleaning {cache_dir}...")
                shutil.rmtree(cache_dir, ignore_errors=True)
                os.makedirs(cache_dir, exist_ok=True)
                run_command(f"chown -R {user}:{user} {cache_dir}", shell=True)
        print("✅ Temporary files cleaned successfully")
        return True
    except Exception as e:
        print_error(f"Failed to clean temporary files: {e}")
        return False

def fix_user_permissions(user: str) -> bool:
    print("→ Fixing file permissions...")
    try:
        user_home = f"/home/{user}"
        print(f"→ Setting ownership to {user}:{user}...")
        run_command(f"chown -R {user}:{user} {user_home}", shell=True)
        print(f"→ Setting proper permissions...")
        run_command(f"chmod -R u+rwX {user_home}", shell=True)
        print("✅ File permissions fixed successfully")
        return True
    except Exception as e:
        print_error(f"Failed to fix permissions: {e}")
        return False

def create_project_directories(user: str) -> bool:
    print("→ Creating project directories...")
    try:
        user_home = f"/home/{user}"
        cb_projects = f"{user_home}/cb_projects"
        os.makedirs(cb_projects, exist_ok=True)
        for subdir in ["bin", "bin/Debug", "bin/Release"]:
            path = f"{cb_projects}/{subdir}"
            os.makedirs(path, exist_ok=True)
        run_command(f"chown -R {user}:{user} {cb_projects}", shell=True)
        run_command(f"chmod -R 755 {cb_projects}", shell=True)
        desktop_dir = f"{user_home}/Desktop"
        os.makedirs(desktop_dir, exist_ok=True)
        run_command(f"chown {user}:{user} {desktop_dir}", shell=True)
        print("✅ Project directories created successfully")
        return True
    except Exception as e:
        print_error(f"Failed to create project directories: {e}")
        return False

def add_user_to_groups(user: str) -> bool:
    print("→ Adding user to groups...")
    try:
        groups = ["adm", "dialout", "cdrom", "floppy", "audio", "dip", "video", "plugdev", "netdev"]
        for group in groups:
            try:
                run_command(f"usermod -aG {group} {user}", shell=True, check=False)
            except:
                pass
        print("✅ User added to necessary groups")
        return True
    except Exception as e:
        print_error(f"Failed to add user to groups: {e}")
        return False

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

def rule_exists(chain, table, match_args):
    try:
        result = subprocess.run(["iptables", "-t", table, "-S", chain], capture_output=True, text=True)
        return any(all(arg in line for arg in match_args) for line in result.stdout.splitlines())
    except Exception:
        return False

def remove_old_restrictions(user, verbose=False):
    import pwd
    try:
        uid = pwd.getpwnam(user).pw_uid
    except Exception:
        print(f"❌ User {user} not found.")
        return
    if verbose:
        print(f"[remove_old_restrictions] Flushing iptables/ip6tables rules for user {user} (uid={uid})")
    match_args = ["-m owner", f"--uid-owner {uid}", "-j DROP"]
    if rule_exists("OUTPUT", "filter", match_args):
        subprocess.run(["iptables", "-D", "OUTPUT", "-m", "owner", "--uid-owner", str(uid), "-j", "DROP"], check=False)
    if rule_exists("OUTPUT", "filter", match_args):
        subprocess.run(["ip6tables", "-D", "OUTPUT", "-m", "owner", "--uid-owner", str(uid), "-j", "DROP"], check=False)
    print(f"Old restrictions removed for user: {user}")

def fix_permissions_and_keyring(user, verbose=False):
    fix_vscode_keyring(user)
    fix_codeblocks_permissions(user)
    fix_user_permissions(user)
    create_project_directories(user)
    add_user_to_groups(user)
    subprocess.run(['chmod', '-R', 'u+rwX,g+rX,o+rX', f'/home/{user}'], check=False)

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

def create_backup(user, verbose=False):
    backup_path = f"/home/{user}_backup_$(date +%Y%m%d%H%M%S).tar.gz"
    subprocess.run(["tar", "-czf", backup_path, f"/home/{user}"], check=False)
    print(f"Backup created at {backup_path}")

def create_periodic_refresh_service(username: str, interval_minutes: int = 30):
    service_name = f"contest-refresh-{username}.service"
    timer_name = f"contest-refresh-{username}.timer"
    service_path = Path(f"/etc/systemd/system/{service_name}")
    timer_path = Path(f"/etc/systemd/system/{timer_name}")
    exec_cmd = f"/usr/bin/contest-manager restrict {username}"
    service_content = f"""[Unit]\nDescription=Contest Environment Periodic Restriction Refresh for {username}\nAfter=network.target\n\n[Service]\nType=oneshot\nExecStart={exec_cmd}\n\n[Install]\nWantedBy=multi-user.target\n"""
    timer_content = f"""[Unit]\nDescription=Timer for periodic contest restriction refresh ({interval_minutes} min)\n\n[Timer]\nOnBootSec=5min\nOnUnitActiveSec={interval_minutes}min\n\n[Install]\nWantedBy=timers.target\n"""
    try:
        with open(service_path, 'w') as f:
            f.write(service_content)
        with open(timer_path, 'w') as f:
            f.write(timer_content)
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "enable", timer_name], check=True)
        subprocess.run(["systemctl", "start", timer_name], check=True)
        print(f"Periodic refresh service and timer created: {service_path}, {timer_path}")
    except Exception as e:
        print(f"Failed to create/enable periodic refresh service/timer: {e}")

def install_periodic_refresh(username: str, interval_minutes: int = 30):
    print(f"* Setting up periodic dependency refresh every {interval_minutes} minutes for '{username}'")
    create_periodic_refresh_service(username, interval_minutes)
