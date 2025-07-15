"""
Restriction Controller Utility
Provides a single entry point to apply all contest restrictions for a user.
"""
import sys
from pathlib import Path
from .blacklist_restrictor import block_domains_with_iptables, remove_all_blacklist_iptables
from .usb_restrictor import apply_usb_restrictions, remove_usb_restrictions
from .common import print_header, print_status, print_error, print_step

def apply_all_restrictions(username, config_dir, verbose=False):
    """
    Apply all contest restrictions (network and USB) for a user.
    Returns True if successful, False otherwise.
    """
    config_dir = Path(config_dir)
    blacklist_file = config_dir / "blacklist.txt"
    print_header(f"Applying restrictions for user '{username}' (blacklist mode)")
    # 0. Remove all previous restrictions (network and USB)
    print_step(0, "Clearing all previous restrictions")
    remove_all_blacklist_iptables(username)
    remove_usb_restrictions(username)
    # 1. Block blacklisted domains
    print_step(1, "Blocking blacklisted domains")
    if not block_domains_with_iptables(username, blacklist_file):
        print_error("Failed to apply blacklist network restrictions")
        return False
    # 2. Block USB storage devices
    print_step(2, "Blocking USB storage devices")
    if not apply_usb_restrictions(username):
        print_error("Failed to apply USB restrictions")
        return False
    print_status(f"✅ Restrictions applied successfully for user '{username}' (blacklist mode)")
    return True
