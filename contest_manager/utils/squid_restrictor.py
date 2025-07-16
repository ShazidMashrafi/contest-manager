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
    # Remove overlapping subdomains: if .google.com is present, remove .drive.google.com, etc.
    def is_subdomain(sub, dom):
        return sub != dom and sub.endswith(dom)
    filtered = set(expanded)
    for d1 in expanded:
        for d2 in expanded:
            if is_subdomain(d1, d2):
                if d2 in filtered:
                    filtered.discard(d1)
    with open(SQUID_BLACKLIST_PATH, 'w') as f:
        for d in sorted(filtered):
            f.write(d + '\n')
    print_status(f"Squid blacklist ACL generated at {SQUID_BLACKLIST_PATH}")
    return True

# Helper: Write main squid.conf with blacklist ACL
def write_squid_conf():
    conf = f"""
http_port 3128
http_port 3128 transparent
acl blocked dstdomain "/etc/squid/blacklist.acl"
http_access deny blocked
http_access allow all

# Required minimum config
cache_dir ufs /var/spool/squid 100 16 256
cache deny all
access_log /var/log/squid/access.log
cache_log /var/log/squid/cache.log
pid_filename /var/run/squid/squid.pid
coredump_dir /var/spool/squid
visible_hostname contest-squid
"""
    # Ensure log and coredump directories exist and correct permissions
    import os
    import pwd
    os.makedirs('/var/log/squid', exist_ok=True)
    os.makedirs('/var/spool/squid', exist_ok=True)
    os.makedirs('/var/run/squid', exist_ok=True)
    # Set permissions for squid user if exists, recursively for /var/spool/squid and /var/run/squid
    try:
        import shutil
        squid_uid = pwd.getpwnam('proxy').pw_uid
        squid_gid = pwd.getpwnam('proxy').pw_gid
        os.chown('/var/log/squid', squid_uid, squid_gid)
        os.chown('/var/run/squid', squid_uid, squid_gid)
        for root, dirs, files in os.walk('/var/spool/squid'):
            os.chown(root, squid_uid, squid_gid)
            for d in dirs:
                os.chown(os.path.join(root, d), squid_uid, squid_gid)
            for f in files:
                os.chown(os.path.join(root, f), squid_uid, squid_gid)
    except Exception:
        pass
    with open(SQUID_CONF_PATH, 'w') as f:
        f.write(conf)
    print_status(f"Squid config written to {SQUID_CONF_PATH}")

# Helper: Reload Squid and check for errors, raise if fails
def reload_squid():
    try:
        import os
        import pwd
        squid_uid = pwd.getpwnam('proxy').pw_uid
        squid_gid = pwd.getpwnam('proxy').pw_gid
        # Always initialize cache as proxy user
        subprocess.run(["sudo", "-u", "proxy", "squid", "-z"], check=True)
        # Always ensure permissions are correct before parse/restart
        for root, dirs, files in os.walk('/var/spool/squid'):
            os.chown(root, squid_uid, squid_gid)
            for d in dirs:
                os.chown(os.path.join(root, d), squid_uid, squid_gid)
            for f in files:
                os.chown(os.path.join(root, f), squid_uid, squid_gid)
        result = subprocess.run(["squid", "-k", "parse", "-f", SQUID_CONF_PATH], capture_output=True, text=True)
        if result.returncode != 0:
            print_error(f"❌ Squid config error: {result.stderr.strip()}")
            raise RuntimeError("Squid config parse failed")
        restart_result = subprocess.run(["systemctl", "restart", "squid"], capture_output=True, text=True)
        if restart_result.returncode != 0:
            print_error(f"❌ Squid service failed to start: {restart_result.stderr.strip()}")
            # Only print systemctl status and journalctl logs if user is running with --verbose
            import sys
            if '--verbose' in sys.argv:
                status = subprocess.run(["systemctl", "status", "squid.service"], capture_output=True, text=True)
                print_error(f"systemctl status squid.service:\n{status.stdout}\n{status.stderr}")
                journal = subprocess.run(["journalctl", "-xeu", "squid.service", "--no-pager", "-n", "50"], capture_output=True, text=True)
                print_error(f"journalctl -xeu squid.service:\n{journal.stdout}\n{journal.stderr}")
            raise RuntimeError("Squid service failed to start. See above for details.")
        print_status("✅ Squid service restarted.")
    except Exception as e:
        print_error(f"❌ Failed to restart squid: {e}")
        raise

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
    print_status("Removing iptables redirects for Squid...")
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
    print_status("iptables redirects removed.")

def remove_squid_restrictions():
    print_status("🧹 Removing all Squid network restrictions...")
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
    print_status("✅ Squid restrictions removed.")
