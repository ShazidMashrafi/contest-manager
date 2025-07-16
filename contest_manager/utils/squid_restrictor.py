"""
Squid Restrictor Utility
Handles Squid ACL config, reload, and iptables redirect for transparent proxy restrictions.
"""
import subprocess
from pathlib import Path
from .common import print_status, print_error, print_warning

SQUID_CONF_PATH = "/etc/squid/squid.conf"
SQUID_BLACKLIST_PATH = "/etc/squid/blacklist.acl"

# Helper: Generate Squid ACL from blacklist file
def generate_squid_acl(blacklist_file):
    if not Path(blacklist_file).exists():
        print_error(f"Blacklist file not found: {blacklist_file}")
        return False
    with open(blacklist_file) as f:
        domains = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    # Expand subdomains and country domains
    expanded = set()
    for domain in domains:
        expanded.add(domain)
        if not domain.startswith('.'):
            expanded.add('.' + domain)
        if not domain.startswith('www.'):
            expanded.add('www.' + domain)
    with open(SQUID_BLACKLIST_PATH, 'w') as f:
        for d in sorted(expanded):
            f.write(d + '\n')
    print_status(f"Squid blacklist ACL generated at {SQUID_BLACKLIST_PATH}")
    return True

# Helper: Write main squid.conf with blacklist ACL
def write_squid_conf():
    conf = f"""
http_port 3128 transparent
acl blocked dstdomain "/etc/squid/blacklist.acl"
http_access deny blocked
http_access allow all
"""
    with open(SQUID_CONF_PATH, 'w') as f:
        f.write(conf)
    print_status(f"Squid config written to {SQUID_CONF_PATH}")

# Helper: Reload Squid
def reload_squid():
    try:
        subprocess.run(["systemctl", "restart", "squid"], check=True)
        print_status("Squid service restarted.")
    except Exception as e:
        print_error(f"Failed to restart squid: {e}")

# Helper: Set up iptables redirect for transparent proxy
def setup_iptables_redirect():
    # Remove old rules first
    remove_iptables_redirect()
    # Redirect all HTTP (80) and HTTPS (443) to squid
    try:
        subprocess.run(["iptables", "-t", "nat", "-A", "PREROUTING", "-p", "tcp", "--dport", "80", "-j", "REDIRECT", "--to-port", "3128"], check=True)
        print_status("iptables redirect for HTTP set.")
    except Exception as e:
        print_warning(f"Failed to set iptables HTTP redirect: {e}")
    # For HTTPS, Squid must be configured for SSL Bump (advanced, not default)
    # Optionally block all 443 if not using SSL Bump
    try:
        subprocess.run(["iptables", "-A", "OUTPUT", "-p", "tcp", "--dport", "443", "-j", "REJECT"], check=False)
        print_status("iptables blocks HTTPS (443) by default.")
    except Exception as e:
        print_warning(f"Failed to block HTTPS: {e}")

def remove_iptables_redirect():
    # Remove all PREROUTING rules for port 3128
    try:
        while True:
            result = subprocess.run(["iptables", "-t", "nat", "-L", "PREROUTING", "--line-numbers"], capture_output=True, text=True)
            lines = result.stdout.splitlines()
            found = False
            for line in lines:
                if "REDIRECT" in line and "3128" in line:
                    num = line.split()[0]
                    subprocess.run(["iptables", "-t", "nat", "-D", "PREROUTING", num], check=False)
                    found = True
                    break
            if not found:
                break
    except Exception:
        pass
    # Remove OUTPUT block for 443
    try:
        while True:
            result = subprocess.run(["iptables", "-L", "OUTPUT", "--line-numbers"], capture_output=True, text=True)
            lines = result.stdout.splitlines()
            found = False
            for line in lines:
                if "REJECT" in line and "443" in line:
                    num = line.split()[0]
                    subprocess.run(["iptables", "-D", "OUTPUT", num], check=False)
                    found = True
                    break
            if not found:
                break
    except Exception:
        pass

def remove_squid_restrictions():
    remove_iptables_redirect()
    try:
        subprocess.run(["systemctl", "stop", "squid"], check=False)
        print_status("Squid service stopped.")
    except Exception:
        pass
    for f in [SQUID_CONF_PATH, SQUID_BLACKLIST_PATH]:
        try:
            Path(f).unlink()
        except Exception:
            pass
    print_status("Squid restrictions removed.")
