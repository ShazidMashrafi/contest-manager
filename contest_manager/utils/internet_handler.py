"""
Internet restriction utilities for contest-manager
"""
import pwd
import subprocess
import dns.resolver
from pathlib import Path
import json

def get_subdomains(domain):
    """Generate common subdomain names for a domain."""
    common_subs = ["www", "mail", "drive", "chat", "api", "blog", "m", "app", "cdn", "static", "dev", "test"]
    return [f"{sub}.{domain}" for sub in common_subs]

def resolve_ips(domain):
    """Resolve all IPv4 and IPv6 addresses for a domain and its subdomains."""
    ips = set()
    try:
        answers = dns.resolver.resolve(domain, 'A')
        for rdata in answers:
            ips.add(str(rdata))
    except Exception:
        pass
    try:
        answers = dns.resolver.resolve(domain, 'AAAA')
        for rdata in answers:
            ips.add(str(rdata))
    except Exception:
        pass
    return ips

def store_ip_cache(user, blacklist_path, cache_path, verbose=False):
    """
    Generate subdomains, resolve IPs, and store all results in a cache file.
    """
    if verbose:
        print(f"[store_ip_cache] Reading blacklist from {blacklist_path}")
    if not Path(blacklist_path).exists():
        print(f"❌ Blacklist file {blacklist_path} not found.")
        return False
    domains = []
    with open(blacklist_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                domains.append(line)
    if not domains:
        print("⚠️  No domains found in blacklist. Skipping IP cache.")
        return False
    allow_patterns = ['static.', 'cdn.', 'fonts.']
    targets = []
    for domain in domains:
        if any(domain.startswith(p) for p in allow_patterns):
            continue
        targets.append(domain)
        targets.extend(get_subdomains(domain))
    ip_map = {}
    for target in targets:
        ip_map[target] = list(resolve_ips(target))
    with open(cache_path, 'w') as f:
        json.dump(ip_map, f, indent=2)
    if verbose:
        print(f"IP cache saved to {cache_path}")
    return True

def apply_restrictions_from_cache(user, cache_path, verbose=False):
    """
    Apply iptables/ip6tables rules for all cached IPs for the user.
    """
    if not Path(cache_path).exists():
        print(f"❌ IP cache file {cache_path} not found.")
        return False
    try:
        uid = pwd.getpwnam(user).pw_uid
    except Exception:
        print(f"❌ User {user} not found.")
        return False
    with open(cache_path) as f:
        ip_map = json.load(f)
    for target, ips in ip_map.items():
        for ip in ips:
            try:
                if ':' in ip:
                    subprocess.run(["ip6tables", "-A", "OUTPUT", "-d", ip, "-m", "owner", "--uid-owner", str(uid), "-j", "DROP"], check=True)
                else:
                    subprocess.run(["iptables", "-A", "OUTPUT", "-d", ip, "-m", "owner", "--uid-owner", str(uid), "-j", "DROP"], check=True)
            except Exception:
                pass
        # Block DNS requests for the domain/subdomain
        try:
            subprocess.run(["iptables", "-A", "OUTPUT", "-p", "udp", "--dport", "53", "-m", "string", "--string", target, "--algo", "bm", "-m", "owner", "--uid-owner", str(uid), "-j", "DROP"], check=True)
        except Exception:
            pass
        # Block DNS over HTTPS (DoH) for the domain/subdomain (TCP 443)
        try:
            subprocess.run(["iptables", "-A", "OUTPUT", "-p", "tcp", "--dport", "443", "-m", "string", "--string", target, "--algo", "bm", "-m", "owner", "--uid-owner", str(uid), "-j", "DROP"], check=True)
            subprocess.run(["ip6tables", "-A", "OUTPUT", "-p", "tcp", "--dport", "443", "-m", "string", "--string", target, "--algo", "bm", "-m", "owner", "--uid-owner", str(uid), "-j", "DROP"], check=True)
        except Exception:
            pass
    if verbose:
        print(f"Applied restrictions for user {user} from cache {cache_path}")
    print("✅ Internet restrictions applied for user from cache.")
    return True

def restrict_internet(user, blacklist_path, cache_path=None, verbose=False):
    """
    Restrict internet access for the given user based on blacklist file.
    Uses store_ip_cache and apply_restrictions_from_cache.
    """
    if not cache_path:
        print("❌ cache_path must be provided.")
        return False
    success = store_ip_cache(user, blacklist_path, cache_path, verbose=verbose)
    if not success:
        print("Failed to store IP cache. No restrictions applied.")
        return False
    return apply_restrictions_from_cache(user, cache_path, verbose=verbose)

def unrestrict_internet(user, blacklist_path, verbose=False):
    """
    Remove internet restrictions for the given user based on blacklist file.
    Deletes iptables/ip6tables rules for all domains and subdomains listed in the blacklist.
    """
    print(f"🔓 Unrestricting all internet restrictions for user: {user}")
    try:
        uid = pwd.getpwnam(user).pw_uid
    except Exception:
        print(f"❌ User {user} not found.")
        return
    # Remove all iptables OUTPUT DROP rules for this UID
    for table in ["iptables", "ip6tables"]:
        try:
            # List all rules
            result = subprocess.run([table, "-S", "OUTPUT"], capture_output=True, text=True)
            rules = result.stdout.splitlines()
            for rule in rules:
                if f"-m owner --uid-owner {uid}" in rule and "-j DROP" in rule:
                    # Convert rule to delete command
                    delete_cmd = [table, "-D", "OUTPUT"] + rule.replace(f"-A OUTPUT ", "").split()
                    # Check if rule exists before attempting to delete
                    check_result = subprocess.run([table, "-C", "OUTPUT"] + rule.replace(f"-A OUTPUT ", "").split(), capture_output=True)
                    if check_result.returncode == 0:
                        try:
                            subprocess.run(delete_cmd, check=False)
                            if verbose:
                                print(f"Removed rule: {table} {' '.join(delete_cmd)}")
                        except Exception:
                            pass
        except Exception:
            pass
    print("✅ All internet restrictions removed for user.")


def internet_restriction_check(user):
    """
    Check if internet restriction is applied for the given user (any iptables/ip6tables OUTPUT DROP rules for UID).
    Returns True if any such rule exists, False otherwise.
    """
    try:
        uid = pwd.getpwnam(user).pw_uid
    except Exception:
        print(f"❌ User {user} not found.")
        return False
    for table in ["iptables", "ip6tables"]:
        try:
            result = subprocess.run([table, "-S", "OUTPUT"], capture_output=True, text=True)
            rules = result.stdout.splitlines()
            for rule in rules:
                if f"-m owner --uid-owner {uid}" in rule and "-j DROP" in rule:
                    return True
        except Exception:
            pass
    return False