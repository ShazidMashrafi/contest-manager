import subprocess
from pathlib import Path

def start_persistence(user):
    """
    Set up systemd service and timer to persist contest restrictions for the given user.
    Uses global contest-manager CLI commands for start-restriction and update-restriction.
    """
    systemd_dir = Path('/etc/systemd/system')
    cli_cmd = 'contest-manager'

    # Service to run start-restriction at boot
    start_service = f"""
[Unit]
Description=Contest Start Restriction for user {user}
After=network.target

[Service]
Type=oneshot
    ExecStart=contest-manager start-restriction {user}
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
"""
    start_service_path = systemd_dir / f"contest-start-restriction-{user}.service"
    with open(start_service_path, 'w') as f:
        f.write(start_service)

    # Service to run update-restriction
    update_service = f"""
[Unit]
Description=Contest Update Restriction for user {user}
After=network.target

[Service]
Type=oneshot
    ExecStart=contest-manager update-restriction {user}
"""
    update_service_path = systemd_dir / f"contest-update-restriction-{user}.service"
    with open(update_service_path, 'w') as f:
        f.write(update_service)

    # Timer to run update-restriction every 30 minutes
    update_timer = f"""
[Unit]
Description=Contest Update Restriction Timer for user {user}

[Timer]
OnBootSec=5min
OnUnitActiveSec=30min
Unit=contest-update-restriction-{user}.service

[Install]
WantedBy=timers.target
"""
    update_timer_path = systemd_dir / f"contest-update-restriction-{user}.timer"
    with open(update_timer_path, 'w') as f:
        f.write(update_timer)

    # Reload systemd and enable/start units
    subprocess.run(['systemctl', 'daemon-reload'], check=True)
    subprocess.run(['systemctl', 'enable', f'contest-start-restriction-{user}.service'], check=True)
    subprocess.run(['systemctl', 'start', f'contest-start-restriction-{user}.service'], check=True)
    subprocess.run(['systemctl', 'enable', f'contest-update-restriction-{user}.timer'], check=True)
    subprocess.run(['systemctl', 'start', f'contest-update-restriction-{user}.timer'], check=True)
    print(f"✅ Persistence enabled: start-restriction at boot, update-restriction every 30 min for user {user}")


def remove_persistence(user):
    """
    Remove systemd service and timer for contest restrictions for the given user.
    """
    systemd_dir = Path('/etc/systemd/system')
    start_service_path = systemd_dir / f"contest-start-restriction-{user}.service"
    update_service_path = systemd_dir / f"contest-update-restriction-{user}.service"
    update_timer_path = systemd_dir / f"contest-update-restriction-{user}.timer"

    # Stop and disable units
    subprocess.run(['systemctl', 'stop', f'contest-update-restriction-{user}.timer'], check=False)
    subprocess.run(['systemctl', 'disable', f'contest-update-restriction-{user}.timer'], check=False)
    subprocess.run(['systemctl', 'stop', f'contest-update-restriction-{user}.service'], check=False)
    subprocess.run(['systemctl', 'disable', f'contest-update-restriction-{user}.service'], check=False)
    subprocess.run(['systemctl', 'stop', f'contest-start-restriction-{user}.service'], check=False)
    subprocess.run(['systemctl', 'disable', f'contest-start-restriction-{user}.service'], check=False)

    # Remove unit files
    for path in [start_service_path, update_service_path, update_timer_path]:
        try:
            path.unlink()
        except FileNotFoundError:
            pass

    # Reload systemd
    subprocess.run(['systemctl', 'daemon-reload'], check=True)
    print(f"✅ Persistence removed for user {user}")