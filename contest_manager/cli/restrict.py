#!/usr/bin/env python3
"""
Contest Environment Restrict CLI
"""
import sys
import argparse
from pathlib import Path

# Import utility functions (to be implemented/extended in utils)
from ..utils.common import check_root
from ..utils.system_utils import remove_old_restrictions, persist_restrictions, schedule_ip_update
from ..utils.usb_restrictor import restrict_usb_storage
from ..utils.blacklist_restrictor import restrict_internet

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

    print("\n🧹 STEP 1: Remove Previous Restrictions\n" + ("="*40))
    remove_old_restrictions(args.user, verbose=args.verbose)
    print("✅ Previous restrictions removed.\n")

    print("\n🌐 STEP 2: Restrict Internet Access\n" + ("="*40))
    restrict_internet(args.user, BLACKLIST_TXT, verbose=args.verbose)
    print("✅ Internet access restricted.\n")

    print("\n🔌 STEP 3: Block USB Storage Devices\n" + ("="*40))
    restrict_usb_storage(args.user, verbose=args.verbose)
    print("✅ USB storage devices blocked.\n")

    print("\n🔒 STEP 4: Make Restrictions Persistent\n" + ("="*40))
    persist_restrictions(args.user, verbose=args.verbose)
    print("✅ Restrictions persistence setup.\n")

    print("\n⏰ STEP 5: Schedule IP Block Updates\n" + ("="*40))
    schedule_ip_update(args.user, BLACKLIST_TXT, verbose=args.verbose)
    print("✅ IP block update scheduled.\n")

    print("\n🎉✅ Restrictions applied successfully!")
    sys.exit(0)

if __name__ == "__main__":
    main()
