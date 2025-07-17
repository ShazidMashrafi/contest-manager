#!/usr/bin/env python3
"""
Contest Environment Status CLI
"""
#!/usr/bin/env python3
"""
Contest Environment Status CLI
"""
import sys
import argparse
from ..utils.usb_handler import usb_restriction_check
from ..utils.internet_handler import internet_restriction_check

def create_parser():
    parser = argparse.ArgumentParser(
        description="Show current restriction status for a user",
        prog="contest-status"
    )
    parser.add_argument(
        'user', nargs='?', default='participant', help='Username to check (default: participant)'
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true', help='Enable verbose output'
    )
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    user = args.user
    print(f"\n🔎 Restriction Status for user: {user}\n" + ("="*40))
    net_status = internet_restriction_check(user)
    print(f"  Internet restrictions: {'✅ Active' if net_status else '❌ Inactive'}")
    usb_status = usb_restriction_check(user)
    print(f"  USB restrictions: {'✅ Active' if usb_status else '❌ Inactive'}")
    print("\nStatus check complete.\n")

if __name__ == "__main__":
    main()
