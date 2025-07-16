#!/usr/bin/env python3
"""
Contest Environment Unrestrict CLI (Squid Proxy System)
"""

import sys
import argparse
import subprocess
from ..utils.common import check_root, get_project_root
from pathlib import Path
from ..utils.squid_restrictor import remove_squid_restrictions
from ..utils.usb_restrictor import remove_usb_restrictions

SYSTEMD_SERVICE_NAME = "contest_restriction.service"
SYSTEMD_TIMER_NAME = "contest_restriction.timer"

def get_systemd_unit_paths():
    service_path = f"/etc/systemd/system/{SYSTEMD_SERVICE_NAME}"
    timer_path = f"/etc/systemd/system/{SYSTEMD_TIMER_NAME}"
    return service_path, timer_path

def remove_systemd_service():
    service_path, timer_path = get_systemd_unit_paths()
    try:
        subprocess.run(["systemctl", "disable", "--now", SYSTEMD_TIMER_NAME], check=True)
    except Exception:
        pass
    for path in [service_path, timer_path]:
        try:
            if Path(path).exists():
                Path(path).unlink()
        except Exception:
            pass
    subprocess.run(["systemctl", "daemon-reload"], check=True)

def main():
    parser = argparse.ArgumentParser(
        description="Disable all internet and USB restrictions for contest environment",
        prog="contest-unrestrict"
    )
    parser.add_argument(
        'user',
        nargs='?',
        default='participant',
        help='Username to unrestrict (default: participant)'
    )
    parser.add_argument(
        '--config-dir',
        type=str,
        help='Configuration directory path (default: project root)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    args = parser.parse_args()
    check_root()
    try:
        print("\n🧹 Step 1: Removing Squid Proxy and Network Restrictions...")
        remove_squid_restrictions()
        print(f"   ✅ Network (proxy) restrictions removed.")

        print("\n🧹 Step 2: Removing USB Storage Restrictions...")
        remove_usb_restrictions(args.user)
        print(f"   ✅ USB storage restrictions removed for user '{args.user}'.")

        print("\n🧹 Step 3: Removing persistent systemd service/timer...")
        remove_systemd_service()
        print("   ✅ Systemd service and timer removed.")

        print(f"\n🎉 All contest restrictions have been REMOVED for user '{args.user}'.\n")
        sys.exit(0)
    except KeyboardInterrupt:
        print("\nUnrestriction cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unrestriction error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
