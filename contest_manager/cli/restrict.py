#!/usr/bin/env python3
"""
Contest Environment Restrict CLI
"""
import sys
from pathlib import Path
from ..utils.squid_restrictor import generate_squid_acl, write_squid_conf, reload_squid, setup_iptables_redirect, remove_squid_restrictions
from ..utils.usb_restrictor import apply_usb_restrictions, remove_usb_restrictions
import subprocess

SYSTEMD_SERVICE_NAME = "contest_restriction.service"
SYSTEMD_TIMER_NAME = "contest_restriction.timer"



def get_systemd_unit_paths():
    service_path = f"/etc/systemd/system/{SYSTEMD_SERVICE_NAME}"
    timer_path = f"/etc/systemd/system/{SYSTEMD_TIMER_NAME}"
    return service_path, timer_path

def write_systemd_service(username, config_dir):
    service_path, timer_path = get_systemd_unit_paths()
    python_exec = sys.executable
    restrict_script = __file__
    service_content = f"""[Unit]\nDescription=Contest Restriction Service\nAfter=network.target\n\n[Service]\nType=oneshot\nExecStart={python_exec} {restrict_script} {username} --config-dir {config_dir}\n\n[Install]\nWantedBy=multi-user.target\n"""
    timer_content = f"""[Unit]\nDescription=Contest Restriction Timer\n\n[Timer]\nOnBootSec=1min\nOnUnitActiveSec=30min\nUnit={SYSTEMD_SERVICE_NAME}\n\n[Install]\nWantedBy=timers.target\n"""
    with open(service_path, "w") as f:
        f.write(service_content)
    with open(timer_path, "w") as f:
        f.write(timer_content)
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "enable", "--now", SYSTEMD_TIMER_NAME], check=True)

def remove_all_restrictions(username):
    remove_squid_restrictions()
    remove_usb_restrictions(username)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Apply contest restrictions to a user (Squid proxy mode)")
    parser.add_argument('user', help='Username to restrict')
    parser.add_argument('--config-dir', type=str, help='Configuration directory path (default: config/)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    username = args.user
    config_dir = args.config_dir if args.config_dir else str(Path(__file__).parent.parent.parent / "config")

    print("\n🧹 Step 1: Clearing previous restrictions...")
    print("   This may take a few moments if previous restrictions are being removed...")
    remove_all_restrictions(username)
    print("   ✅ Previous restrictions cleared.")

    print("\n🌐 Step 2: Enabling internet restrictions...")
    blacklist_file = Path(config_dir) / "blacklist.txt"
    if not generate_squid_acl(blacklist_file):
        print("❌ Failed to generate Squid blacklist ACL. Aborting.")
        sys.exit(1)
    write_squid_conf()
    try:
        reload_squid()
    except Exception:
        print("❌ Squid service failed to start due to configuration or system error. Restriction not applied.")
        sys.exit(1)
    setup_iptables_redirect()

    print("\n🔒 Step 3: Blocking USB storage devices...")
    apply_usb_restrictions(username)

    print("\n💾 Step 4: Enabling persistent restrictions (systemd)...")
    write_systemd_service(username, config_dir)

    print("\n🎉 All contest restrictions are now ACTIVE and will persist automatically!\n✅ Systemd service and timer set up. Restrictions will persist and update every 30 minutes.\n")

if __name__ == "__main__":
    main()
