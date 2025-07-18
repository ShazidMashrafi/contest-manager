#!/usr/bin/env python3
"""
Contest Environment Update CLI
"""
import sys
from pathlib import Path

from contest_manager.utils.utils import check_root
from contest_manager.utils.internet_handler import update_ip_cache

CONFIG_DIR = Path(__file__).parent.parent.parent / 'config'
BLACKLIST_TXT = CONFIG_DIR / 'blacklist.txt'

def main():
    check_root()
    user = 'participant'
    cache_path = CONFIG_DIR / f"ip_cache_{user}.json"
    print("\n🌐 Updating stored IP cache\n" + ("="*40))
    success = update_ip_cache(user, BLACKLIST_TXT, cache_path, verbose=True)
    if success:
        print(f"\n✅ IP cache updated at {cache_path}\n")
    else:
        print("\n❌ Failed to update IP cache.\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
