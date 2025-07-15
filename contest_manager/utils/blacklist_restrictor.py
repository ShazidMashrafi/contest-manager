# Utility to check if network restrictions are active for a user
def is_network_restricted(username: str) -> bool:
    """Check if network restrictions are active for the user (simple check for blacklist rules)."""
    import pwd
    import subprocess
    try:
        uid = pwd.getpwnam(username).pw_uid
    except Exception:
        return False
    found = False
    for ipt in ['iptables', 'ip6tables']:
        try:
            result = subprocess.run([
                ipt, '-L', 'OUTPUT', '-n', '-v'], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                # Check for string match rules
                if f"owner UID match {uid}" in result.stdout and "REJECT" in result.stdout:
                    found = True
                # Check for IP-based rules
                if f"--uid-owner {uid}" in result.stdout and "REJECT" in result.stdout:
                    found = True
        except Exception:
            continue
    return found
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
    import socket
    with open(blacklist_file, 'r') as f:
        domains = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    if not domains:
        print_warning("Blacklist is empty. No domains will be blocked.")
        return True

    # Common country TLDs for major services
    country_tlds = [
        'com', 'co.in', 'com.bd', 'co.uk', 'ca', 'com.au', 'de', 'fr', 'co.jp', 'ru', 'it', 'es', 'nl', 'com.sg', 'com.hk'
    ]
    # Domains for which to expand TLDs
    tld_expand = {'google', 'bing', 'yahoo'}

    expanded_domains = set()
    for domain in domains:
        expanded_domains.add(domain)
        # Add www. subdomain
        if not domain.startswith('www.'):
            expanded_domains.add(f"www.{domain}")
        # Expand TLDs for selected services
        for service in tld_expand:
            if domain.startswith(service + ".") or domain == service:
                for tld in country_tlds:
                    expanded_domains.add(f"{service}.{tld}")
                    expanded_domains.add(f"www.{service}.{tld}")
        # Add string match for subdomains (catch all)
        if '.' in domain:
            expanded_domains.add(f".{domain}")

    for domain in expanded_domains:
        # Block by string match (HTTP/S fallback)
        for ipt in ['iptables', 'ip6tables']:
            try:
                subprocess.run([
                    ipt, '-A', 'OUTPUT', '-m', 'owner', '--uid-owner', str(uid),
                    '-m', 'string', '--algo', 'bm', '--string', domain,
                    '-j', 'REJECT'
                ], check=True)
                print_status(f"Blocked {domain} for user {username} via {ipt} (string match)")
            except Exception as e:
                print_warning(f"Failed to block {domain} with {ipt} (string match): {e}")
        # Resolve all A/AAAA records and block IPs
        try:
            # IPv4
            try:
                ipv4s = socket.gethostbyname_ex(domain)[2]
            except Exception:
                ipv4s = []
            for ip in ipv4s:
                try:
                    subprocess.run([
                        'iptables', '-A', 'OUTPUT', '-m', 'owner', '--uid-owner', str(uid),
                        '-d', ip, '-j', 'REJECT'
                    ], check=True)
                    print_status(f"Blocked {domain} ({ip}) for user {username} via iptables (IPv4)")
                except Exception as e:
                    print_warning(f"Failed to block {domain} ({ip}) via iptables: {e}")
            # IPv6
            try:
                import dns.resolver
                answers = dns.resolver.resolve(domain, 'AAAA')
                ipv6s = [str(rdata) for rdata in answers]
            except Exception:
                ipv6s = []
            for ip in ipv6s:
                try:
                    subprocess.run([
                        'ip6tables', '-A', 'OUTPUT', '-m', 'owner', '--uid-owner', str(uid),
                        '-d', ip, '-j', 'REJECT'
                    ], check=True)
                    print_status(f"Blocked {domain} ({ip}) for user {username} via ip6tables (IPv6)")
                except Exception as e:
                    print_warning(f"Failed to block {domain} ({ip}) via ip6tables: {e}")
        except Exception as e:
            print_warning(f"DNS resolution failed for {domain}: {e}")
    return True


def remove_all_blacklist_iptables(username: str) -> None:
    """Remove all iptables rules for the user that were added for blacklisting."""
    import pwd, subprocess
    try:
        uid = pwd.getpwnam(username).pw_uid
    except Exception as e:
        print_warning(f"User not found: {username} ({e})")
        return
    # Remove all OUTPUT rules for this user with REJECT (string match or IP-based)
    for ipt in ['iptables', 'ip6tables']:
        while True:
            # List all rules with line numbers
            result = subprocess.run([ipt, '-L', 'OUTPUT', '--line-numbers', '-n', '-v'], capture_output=True, text=True, check=False)
            if result.returncode != 0:
                break
            lines = result.stdout.splitlines()
            found = False
            for line in lines:
                # Example line: 'num  pkts bytes target ... owner UID match 1001 ... REJECT ...'
                if f"owner UID match {uid}" in line and "REJECT" in line:
                    parts = line.split()
                    if parts:
                        try:
                            line_num = parts[0]
                            # Delete by line number
                            subprocess.run([ipt, '-D', 'OUTPUT', line_num], check=False, stderr=subprocess.DEVNULL)
                            found = True
                            break  # After deletion, need to re-list
                        except Exception:
                            continue
            if not found:
                break
