import subprocess
from pathlib import Path

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

def install_snap_flatpak(verbose=False):
    cmds = [
        ['apt-get', 'install', '-y', 'snapd'],
        ['apt-get', 'install', '-y', 'flatpak']
    ]
    for cmd in cmds:
        try:
            if verbose:
                print(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
        except Exception as e:
            print(f"Error running {' '.join(cmd)}: {e}")
            raise

def fix_permissions_and_keyring(user, verbose=False):
    from ..system_utils import fix_vscode_keyring, fix_codeblocks_permissions, fix_user_permissions, create_project_directories, add_user_to_groups
    fix_vscode_keyring(user)
    fix_codeblocks_permissions(user)
    fix_user_permissions(user)
    create_project_directories(user)
    add_user_to_groups(user)
    subprocess.run(['chmod', '-R', 'u+rwX,g+rX,o+rX', f'/home/{user}'], check=False)

def create_backup(user, verbose=False):
    backup_path = f"/home/{user}_backup_$(date +%Y%m%d%H%M%S).tar.gz"
    subprocess.run(["tar", "-czf", backup_path, f"/home/{user}"], check=False)
    print(f"Backup created at {backup_path}")

def create_periodic_refresh_service(username: str, interval_minutes: int = 30):
    """
    Create a systemd service and timer to periodically re-analyze dependencies and reapply restrictions for a user.
    """
    service_name = f"contest-refresh-{username}.service"
    timer_name = f"contest-refresh-{username}.timer"
    service_path = Path(f"/etc/systemd/system/{service_name}")
    timer_path = Path(f"/etc/systemd/system/{timer_name}")
    exec_cmd = f"/usr/bin/contest-manager restrict {username}"
    service_content = f"""[Unit]
Description=Contest Environment Periodic Restriction Refresh for {username}
After=network.target

[Service]
Type=oneshot
ExecStart={exec_cmd}

[Install]
WantedBy=multi-user.target
"""
    timer_content = f"""[Unit]
Description=Timer for periodic contest restriction refresh ({interval_minutes} min)

[Timer]
OnBootSec=5min
OnUnitActiveSec={interval_minutes}min

[Install]
WantedBy=timers.target
"""
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
    """
    Public method to install the periodic refresh systemd job for a user.
    """
    print(f"* Setting up periodic dependency refresh every {interval_minutes} minutes for '{username}'")
    create_periodic_refresh_service(username, interval_minutes)
