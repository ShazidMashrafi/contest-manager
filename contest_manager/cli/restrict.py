#!/usr/bin/env python3
"""
Contest Environment Restrict CLI
"""
import sys
import argparse
from pathlib import Path

from contest_manager.utils.utils import check_root
from contest_manager.utils.internet_handler import *
from contest_manager.utils.usb_handler import *

CONFIG_DIR = Path(__file__).parent.parent.parent / 'config'
BLACKLIST_TXT = CONFIG_DIR / 'blacklist.txt'

def create_parser():
    parser = argparse.ArgumentParser(
        description="Restrict contest user environment (network, USB, persistent)",
        prog="contest-restrict"
    )
    parser.add_argument(
        'user', nargs='?', default='participant', help='Username to restrict (default: participant)'
    )
    parser.add_argument(
        '--config-dir', type=str, help='Configuration directory path (default: project root)'
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true', help='Enable verbose output'
    )
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    check_root()
    print("\n🧹 STEP 1: Remove Internet Restriction\n" + ("="*40))
    unrestrict_internet(args.user, BLACKLIST_TXT, verbose=args.verbose)
    print("✅ Internet restriction removed.\n")

    print("\n🧹 STEP 2: Remove USB Restriction\n" + ("="*40))
    unrestrict_usb_storage_device(args.user, verbose=args.verbose)
    print("✅ USB restriction removed.\n")

    print("\n🌐 STEP 3: Restrict Internet Access\n" + ("="*40))
    restrict_internet(args.user, BLACKLIST_TXT, verbose=args.verbose)
    print("✅ Internet access restricted.\n")

    print("\n🔌 STEP 4: Block USB Storage Devices\n" + ("="*40))
    restrict_usb_storage_device(args.user, verbose=args.verbose)
    print("✅ USB storage devices blocked.\n")

    print("\n🎉✅ Restrictions applied successfully!")
    sys.exit(0)

if __name__ == "__main__":
    main()
