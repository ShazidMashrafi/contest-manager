#!/usr/bin/env python3
"""
Contest Environment Update Restrictions CLI
"""
import sys
import argparse
from pathlib import Path

from contest_manager.utils.utils import check_root
from contest_manager.utils.internet_handler import update_ip_cache, apply_restrictions_from_cache

CONFIG_DIR = Path(__file__).parent.parent.parent / 'config'
BLACKLIST_TXT = CONFIG_DIR / 'blacklist.txt'

def create_parser():
    parser = argparse.ArgumentParser(
        description="Update contest internet restrictions from cache",
        prog="contest-update-restriction"
    )
    parser.add_argument(
        'user', nargs='?', default='participant', help='Username to update restrictions for (default: participant)'
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true', help='Enable verbose output'
    )
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    check_root()
    user = args.user
    cache_path = CONFIG_DIR / f"ip_cache_{user}.json"
    print("\n🌐 Updating stored IP cache\n" + ("="*40))
    success = update_ip_cache(user, BLACKLIST_TXT, cache_path, verbose=args.verbose)
    if success:
        print(f"\n✅ IP cache updated at {cache_path}\n")
        print("\n🌐 Re-applying internet restrictions from updated cache\n" + ("="*40))
        apply_restrictions_from_cache(user, cache_path, verbose=args.verbose)
        print("\n✅ Internet restrictions updated and applied from cache.\n")
    else:
        print("\n❌ Failed to update IP cache.\n")
    sys.exit(0)

if __name__ == "__main__":
    main()

