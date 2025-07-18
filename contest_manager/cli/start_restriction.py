#!/usr/bin/env python3
"""
Contest Environment Start CLI
"""

import sys
import argparse
from pathlib import Path

from contest_manager.utils.utils import check_root
from contest_manager.utils.internet_handler import apply_restrictions_from_cache
from contest_manager.utils.usb_handler import restrict_usb_storage_device

CONFIG_DIR = Path(__file__).parent.parent.parent / 'config'
BLACKLIST_TXT = CONFIG_DIR / 'blacklist.txt'

def create_parser():
    parser = argparse.ArgumentParser(
        description="Start contest restrictions (internet, USB) from cache",
        prog="contest-start"
    )
    parser.add_argument(
        'user', nargs='?', default='participant', help='Username to restrict (default: participant)'
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
    print("\n🌐 Applying internet restrictions from cache\n" + ("="*40))
    apply_restrictions_from_cache(user, verbose=args.verbose)
    print("\n🔌 Blocking USB storage devices\n" + ("="*40))
    restrict_usb_storage_device(user, verbose=args.verbose)
    print("\n✅ Internet and USB restrictions applied from cache.\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
