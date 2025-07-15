#!/usr/bin/env python3
"""
Contest Environment Restrict CLI
"""
import sys
import os
from pathlib import Path
from ..utils.common import print_header, print_status, print_error, print_warning, print_step


from ..utils.usb_restrictor import apply_usb_restrictions
from ..utils.blacklist_restrictor import block_domains_with_iptables



def main():
    import argparse
    parser = argparse.ArgumentParser(description="Apply contest restrictions to a user (blacklist mode)")
    parser.add_argument('user', help='Username to restrict')
    parser.add_argument('--config-dir', type=str, help='Configuration directory path (default: config/)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    username = args.user
    config_dir = Path(args.config_dir) if args.config_dir else Path(__file__).parent.parent.parent / "config"
    blacklist_file = config_dir / "blacklist.txt"  # config_dir now should be config/

    print_header(f"Applying restrictions for user '{username}' (blacklist mode)")

    # 0. Remove all previous restrictions (network and USB)
    print_step(0, "Clearing all previous restrictions")
    from ..utils.blacklist_restrictor import remove_all_blacklist_iptables
    remove_all_blacklist_iptables(username)
    from ..utils.usb_restrictor import remove_usb_restrictions
    remove_usb_restrictions(username)

    # 1. Block blacklisted domains
    print_step(1, "Blocking blacklisted domains")
    if not block_domains_with_iptables(username, blacklist_file):
        print_error("Failed to apply blacklist network restrictions")
        sys.exit(1)

    # 2. Block USB storage devices
    print_step(2, "Blocking USB storage devices")
    if not apply_usb_restrictions(username):
        print_error("Failed to apply USB restrictions")
        sys.exit(1)

    print_status(f"✅ Restrictions applied successfully for user '{username}' (blacklist mode)")

if __name__ == "__main__":
    main()
