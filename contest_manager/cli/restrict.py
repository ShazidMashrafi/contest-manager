#!/usr/bin/env python3
"""
Contest Environment Restrict CLI
"""
from pathlib import Path
from ..core.manager import ContestManager
from ..utils.network_restrictor import NetworkRestrictor
from ..utils.usb_restrictor import USBRestrictor
from ..utils.dependency_analyzer import DependencyAnalyzer
import os
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: contest-manager restrict <username>")
        sys.exit(1)
    username = sys.argv[1]
    manager = ContestManager()
    print("="*60)
    print(f"  Applying restrictions for user '{username}'")
    print("="*60)

    # 0. Remove all old iptables/Squid rules and dependency cache
    print("="*50)
    print("Step 0: Clearing old network rules and dependency cache")
    print("="*50)
    restrictor = NetworkRestrictor(username)
    restrictor.clear_existing_rules()
    if os.path.exists(manager.cache_file):
        try:
            os.remove(manager.cache_file)
            print(f"  → Old dependency cache removed: {manager.cache_file}")
        except Exception as e:
            print(f"  ⚠️  Could not remove old dependency cache: {e}")

    # 1. Analyze dependencies for all whitelisted domains
    print("="*50)
    print("Step 1: Analyzing dependencies for whitelisted domains")
    print("="*50)
    whitelist = manager.load_whitelist()
    analyzer = DependencyAnalyzer()
    dependencies = analyzer.analyze_domains_from_file(str(manager.whitelist_file))
    print(f"  → Found {len(dependencies)} dependencies.")

    # 2. Apply network restrictions: allow whitelist + dependencies
    print("="*50)
    print("Step 2: Applying network restrictions")
    print("="*50)
    restrictor.apply_restrictions(whitelist, dependencies)

    # 3. (Blocking all else is implicit in network restrictor logic)

    # 4. Apply USB restrictions
    print("="*50)
    print("Step 3: Applying USB restrictions")
    print("="*50)
    usb_restrictor = USBRestrictor(username)
    usb_restrictor.apply_usb_restrictions()

    print("="*60)
    print(f"  Restrictions applied successfully for user '{username}'")
    print("="*60)

if __name__ == "__main__":
    main()
