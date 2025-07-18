"""
Internet restriction utilities for contest-manager
"""

import pwd
import subprocess
from pathlib import Path

def get_targets_from_blacklist(blacklist_path):
    """
    Read blacklist file and return a list of domains to block (excluding allowed patterns).
    """
    if not Path(blacklist_path).exists():
        print(f"❌ Blacklist file {blacklist_path} not found.")
        return []
    domains = []
    with open(blacklist_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                domains.append(line)
    return domains

def restrict_internet(user, blacklist_path, verbose=False):
    """
    Set up dnsmasq config and minimal firewall rules to block internet access for the user to blacklisted domains and subdomains.
    """
    # 1. Write dnsmasq config for blacklist
    dnsmasq_conf_path = f"/etc/dnsmasq.d/contest-{user}-blacklist.conf"
    targets = get_targets_from_blacklist(blacklist_path)
    allow_patterns = ['static.', 'cdn.', 'fonts.']
    with open(dnsmasq_conf_path, 'w') as f:
        for domain in targets:
            if any(domain.startswith(p) for p in allow_patterns):
                continue
            f.write(f"address=/{domain}/0.0.0.0\n")
            f.write(f"address=/{domain}/::\n")
    if verbose:
        print(f"[dnsmasq] Blacklist config written to {dnsmasq_conf_path}")
    # 2. Restart dnsmasq to apply changes
    subprocess.run(["systemctl", "restart", "dnsmasq"], check=False)
    if verbose:
        print("[dnsmasq] Service restarted.")
    # 3. Add minimal firewall rule to force DNS usage and block direct IP access
    # Example: block all outbound except DNS (port 53)
    subprocess.run(["iptables", "-A", "OUTPUT", "-m", "owner", "--uid-owner", user, "!", "-p", "udp", "--dport", "53", "-j", "DROP"], check=False)
    subprocess.run(["ip6tables", "-A", "OUTPUT", "-m", "owner", "--uid-owner", user, "!", "-p", "udp", "--dport", "53", "-j", "DROP"], check=False)
    if verbose:
        print("[firewall] Minimal rules applied for user.")
    print(f"✅ dnsmasq and firewall restrictions applied for user: {user}")

def unrestrict_internet(user, blacklist_path, verbose=False):
    """
    Remove dnsmasq config and minimal firewall rules for the user.
    """
    dnsmasq_conf_path = f"/etc/dnsmasq.d/contest-{user}-blacklist.conf"
    # Remove dnsmasq config
    try:
        Path(dnsmasq_conf_path).unlink()
        if verbose:
            print(f"[dnsmasq] Blacklist config {dnsmasq_conf_path} removed.")
    except FileNotFoundError:
        if verbose:
            print(f"[dnsmasq] Blacklist config {dnsmasq_conf_path} not found.")
    # Restart dnsmasq
    subprocess.run(["systemctl", "restart", "dnsmasq"], check=False)
    if verbose:
        print("[dnsmasq] Service restarted.")
    # Remove minimal firewall rules
    subprocess.run(["iptables", "-D", "OUTPUT", "-m", "owner", "--uid-owner", user, "!", "-p", "udp", "--dport", "53", "-j", "DROP"], check=False)
    subprocess.run(["ip6tables", "-D", "OUTPUT", "-m", "owner", "--uid-owner", user, "!", "-p", "udp", "--dport", "53", "-j", "DROP"], check=False)
    if verbose:
        print("[firewall] Minimal rules removed for user.")
    print(f"✅ dnsmasq and firewall restrictions removed for user: {user}")


def internet_restriction_check(user):
    """
    Check if the minimal firewall rule for DNS-only access is present for the user.
    Returns True if the rule exists, False otherwise.
    """
    for table in ["iptables", "ip6tables"]:
        try:
            result = subprocess.run([table, "-S", "OUTPUT"], capture_output=True, text=True)
            rules = result.stdout.splitlines()
            for rule in rules:
                # Check for the minimal DNS-only rule for this user
                if f"--uid-owner {user}" in rule and "-j DROP" in rule and "! -p udp --dport 53" in rule:
                    return True
        except Exception:
            pass
    return False