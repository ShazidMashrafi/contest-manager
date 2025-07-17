import os
import subprocess

def persistence_across_reboots(user, blacklist_path, verbose=False):
    """
    Ensure internet and USB restrictions are re-applied after every reboot for the given user.
    Creates a systemd service that runs at boot to re-apply restrictions.
    This does not clear iptables, just re-applies restrictions using the existing rules.
    """
    script_path = f"/usr/local/bin/contest_restrict_{user}_boot.py"
    script_code = f"""
import sys
try:
    from contest_manager.utils.internet_handler import restrict_internet
    from contest_manager.utils.usb_handler import restrict_usb_storage_device
except ImportError:
    import sys, os
    sys.path.append('/usr/local/lib/python3.10/dist-packages')  # Adjust if needed
    from contest_manager.utils.internet_handler import restrict_internet
    from contest_manager.utils.usb_handler import restrict_usb_storage_device
restrict_internet('{user}', '{blacklist_path}', verbose={verbose}, persist=True)
restrict_usb_storage_device('{user}', verbose={verbose})
"""
    with open(script_path, "w") as f:
        f.write(script_code)
    os.chmod(script_path, 0o755)
    service_name = f"contest-restrict-{user}.service"
    service_path = f"/etc/systemd/system/{service_name}"
    service_code = f"""
[Unit]
Description=Contest Restrict (Internet & USB) for user {user} on boot
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 {script_path}
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
"""
    with open(service_path, "w") as f:
        f.write(service_code)
    subprocess.run(["systemctl", "daemon-reload"])
    subprocess.run(["systemctl", "enable", service_name])
    subprocess.run(["systemctl", "start", service_name])
    if verbose:
        print(f"Systemd service for persistence created: {service_path}")
        print(f"Boot script created: {script_path}")

def update_restrictions(user, blacklist_path, verbose=False):
    """
    Ensure internet restrictions are updated every 30 minutes for the given user.
    Creates a systemd timer and service to run restrict_internet (append-only) every 30 minutes.
    This does not clear old iptables rules, just appends new ones if needed.
    USB restrictions are not touched here.
    """
    script_path = f"/usr/local/bin/contest_update_inet_{user}.py"
    script_code = f"""
import sys
try:
    from contest_manager.utils.internet_handler import restrict_internet
except ImportError:
    import sys, os
    sys.path.append('/usr/local/lib/python3.10/dist-packages')  # Adjust if needed
    from contest_manager.utils.internet_handler import restrict_internet
restrict_internet('{user}', '{blacklist_path}', verbose={verbose}, persist=True)
"""
    with open(script_path, "w") as f:
        f.write(script_code)
    os.chmod(script_path, 0o755)
    service_name = f"contest-update-inet-{user}.service"
    service_path = f"/etc/systemd/system/{service_name}"
    service_code = f"""
[Unit]
Description=Contest Update Internet Restrictions for user {user} (every 30 min)
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 {script_path}

[Install]
WantedBy=multi-user.target
"""
    with open(service_path, "w") as f:
        f.write(service_code)
    timer_name = f"contest-update-inet-{user}.timer"
    timer_path = f"/etc/systemd/system/{timer_name}"
    timer_code = f"""
[Unit]
Description=Contest Update Internet Restrictions Timer for user {user}

[Timer]
OnBootSec=5min
OnUnitActiveSec=30min
Unit={service_name}

[Install]
WantedBy=timers.target
"""
    with open(timer_path, "w") as f:
        f.write(timer_code)
    subprocess.run(["systemctl", "daemon-reload"])
    subprocess.run(["systemctl", "enable", timer_name])
    subprocess.run(["systemctl", "start", timer_name])
    if verbose:
        print(f"Systemd timer for updating internet restrictions created: {timer_path}")
        print(f"Update script created: {script_path}")

def ensure_all_persistence(user, blacklist_path, verbose=False):
    """
    Sets up all persistence mechanisms for restrictions for a given user.
    Calls both persistence_across_reboots and update_restrictions.
    """
    persistence_across_reboots(user, blacklist_path, verbose=verbose)
    update_restrictions(user, blacklist_path, verbose=verbose)