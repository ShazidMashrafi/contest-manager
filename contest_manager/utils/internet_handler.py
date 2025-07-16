"""
Internet restriction utilities for contest-manager
"""
import subprocess
from pathlib import Path
import dns.resolver
import pwd

def get_subdomains(domain):
    """Generate common subdomain names for a domain."""
    # This is a static list; for real use, you may want to parse from config or use a DNS enumeration tool
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

def restrict_internet(user, blacklist_path, verbose=False, persist=False):
    """
    Restrict internet access for the given user based on blacklist file.
    Block only the domains and subdomains listed in the blacklist, for both IPv4 and IPv6, and block DNS/DoH for those domains.
    If persist=True, only apply restrictions (for systemd persistence).
    """
    print(f"🌐 Restricting internet access for user: {user}")
    print(f"🌐 It might take a moment... Please sit back and relax.")
    if verbose:
        print(f"[restrict_internet] Reading blacklist from {blacklist_path}")
    if not Path(blacklist_path).exists():
        print(f"❌ Blacklist file {blacklist_path} not found.")
        return
    try:
        uid = pwd.getpwnam(user).pw_uid
    except Exception:
        print(f"❌ User {user} not found.")
        return
    domains = []
    with open(blacklist_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                domains.append(line)
    if not domains:
        print("⚠️  No domains found in blacklist. Skipping internet restriction.")
        return
    blocked = []
    for domain in domains:
        allow_patterns = ['static.', 'cdn.', 'fonts.']
        if any(domain.startswith(p) for p in allow_patterns):
            continue
        # Block domain and common subdomains
        targets = [domain] + get_subdomains(domain)
        for target in targets:
            ips = resolve_ips(target)
            if ips:
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
        blocked.append(domain)
    if blocked:
        print("Blocked domains and subdomains for user:")
        for domain in blocked:
            print(f"  - {domain}")
            subs = get_subdomains(domain)
            for sub in subs:
                print(f"    • {sub}")
    print("✅ Internet restrictions applied for user.")


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

def persist_internet_restrictions(user):
    """
    Persist internet restrictions for the user using systemd service and timer.
    """
    import sys
    import subprocess
    from pathlib import Path
    service_name = f"contest-inet-restrict-{user}.service"
    timer_name = f"contest-inet-restrict-{user}.timer"
    script_path = Path(__file__).parent.parent / "cli" / "restrict.py"
    service_path = f"/etc/systemd/system/{service_name}"
    timer_path = f"/etc/systemd/system/{timer_name}"

    service_content = f"""
[Unit]
Description=Persist internet restrictions for user {user}
After=network.target

[Service]
Type=oneshot
ExecStart={sys.executable} {script_path} {user}
User=root

[Install]
WantedBy=multi-user.target
"""

    timer_content = f"""
[Unit]
Description=Run internet restriction for user {user} every 30 minutes

[Timer]
OnBootSec=1min
OnUnitActiveSec=30min
Unit={service_name}

[Install]
WantedBy=timers.target
"""

    try:
        with open(service_path, "w") as f:
            f.write(service_content)
        with open(timer_path, "w") as f:
            f.write(timer_content)
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "enable", "--now", timer_name], check=True)
        print(f"Systemd internet restriction service and timer created for user {user}.")
        return True
    except Exception as e:
        print(f"Failed to set up internet restriction persistence: {e}")
        return False