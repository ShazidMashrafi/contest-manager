#!/usr/bin/env python3
"""
Contest Environment Restrict CLI
"""
import sys
import os
from pathlib import Path
from ..utils.common import print_header, print_status, print_error, print_warning, print_step
from ..utils.network_restrictor import NetworkRestrictor, apply_network_restrictions
from ..utils.usb_restrictor import USBRestrictor, apply_usb_restrictions
from ..utils.dependency_analyzer import DependencyAnalyzer
from ..utils.setup_utils import create_project_directories

from ..utils.system_utils import clean_temporary_files

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Apply contest restrictions to a user")
    parser.add_argument('user', help='Username to restrict')
    parser.add_argument('--config-dir', type=str, help='Configuration directory path (default: /etc/contest-manager)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    username = args.user
    config_dir = Path(args.config_dir) if args.config_dir else Path("/etc/contest-manager")
    whitelist_file = config_dir / "whitelist.txt"
    cache_file = config_dir / ".dependency_cache.json"

    print_header(f"Applying restrictions for user '{username}'")

    # 0. Remove all old iptables/Squid rules and dependency cache
    print_step(0, "Clearing old network rules and dependency cache")
    restrictor = NetworkRestrictor(username)
    restrictor.clear_existing_rules()
    if cache_file.exists():
        try:
            cache_file.unlink()
            print_status(f"Old dependency cache removed: {cache_file}")
        except Exception as e:
            print_warning(f"Could not remove old dependency cache: {e}")

    # 1. Analyze dependencies for each whitelisted domain
    print_step(1, "Analyzing dependencies for whitelisted domains")
    try:
        analyzer = DependencyAnalyzer()
        if whitelist_file.exists():
            with open(whitelist_file, 'r') as f:
                whitelist = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        else:
            whitelist = []
        dependency_cache = {}
        for domain in whitelist:
            try:
                deps = list(analyzer.analyze_domain(domain, whitelist_domains=whitelist))
                dependency_cache[domain] = deps
            except Exception as e:
                print_warning(f"Dependency analysis failed for {domain}: {e}")
                dependency_cache[domain] = []
        # Save dependency cache
        with open(cache_file, 'w') as f:
            import json
            json.dump(dependency_cache, f, indent=2)
        print_status(f"Dependency cache updated: {cache_file}")
    except Exception as e:
        print_error(f"Dependency analysis failed: {e}")

    # 2. Apply network restrictions (allow whitelist + dependencies, block all else)
    print_step(2, "Applying network restrictions")
    if not apply_network_restrictions(username, str(whitelist_file)):
        print_error("Failed to apply network restrictions")
        sys.exit(1)

    # 3. Apply USB restrictions
    print_step(3, "Applying USB restrictions")
    if not apply_usb_restrictions(username):
        print_error("Failed to apply USB restrictions")
        sys.exit(1)

    print_status(f"✅ Restrictions applied successfully for user '{username}'")

if __name__ == "__main__":
    main()
