#!/usr/bin/env python3
"""
Blacklist-based Network Restrictor Utilities
"""
import pwd
import subprocess
from pathlib import Path
from .common import print_error, print_status, print_warning

def block_domains_with_iptables(username: str, blacklist_file: Path) -> bool:
    """Block access to all domains in blacklist_file for the given user using iptables."""
    if not blacklist_file.exists():
        print_error(f"Blacklist file not found: {blacklist_file}")
        return False
    try:
        uid = pwd.getpwnam(username).pw_uid
    except Exception as e:
        print_error(f"User not found: {username} ({e})")
        return False
    with open(blacklist_file, 'r') as f:
        domains = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    if not domains:
        print_warning("Blacklist is empty. No domains will be blocked.")
        return True
    for domain in domains:
        # Block both IPv4 and IPv6
        for ipt in ['iptables', 'ip6tables']:
            try:
                subprocess.run([
                    ipt, '-A', 'OUTPUT', '-m', 'owner', '--uid-owner', str(uid),
                    '-m', 'string', '--algo', 'bm', '--string', domain,
                    '-j', 'REJECT'
                ], check=True)
                print_status(f"Blocked {domain} for user {username} via {ipt}")
            except Exception as e:
                print_warning(f"Failed to block {domain} with {ipt}: {e}")
    return True


def remove_all_blacklist_iptables(username: str) -> None:
    """Remove all iptables rules for the user that were added for blacklisting."""
    try:
        uid = pwd.getpwnam(username).pw_uid
    except Exception as e:
        print_warning(f"User not found: {username} ({e})")
        return
    for ipt in ['iptables', 'ip6tables']:
        # Remove all OUTPUT rules for this user that use string match and REJECT
        try:
            subprocess.run([
                ipt, '-D', 'OUTPUT', '-m', 'owner', '--uid-owner', str(uid),
                '-j', 'REJECT'
            ], check=False)
        except Exception:
            pass
        # Optionally, flush all OUTPUT rules for this user (could be improved)
