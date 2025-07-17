#!/usr/bin/env python3
"""
Contest Environment Status CLI
"""
import sys
import argparse
from ..utils.common import get_project_root
from ..utils.usb_handler import is_usb_restricted
from ..utils.internet_handler import is_network_restricted

def create_parser():
    parser = argparse.ArgumentParser(
        description="Show current restriction and USB status for a user",
        prog="contest-status"
    )
    parser.add_argument(
        'user', nargs='?', default='participant', help='Username to check (default: participant)'
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
    user = args.user
    config_dir = args.config_dir or get_project_root()
    print(f"Status for user: {user}")
    # Network restriction status
    net_status = is_network_restricted(user)
    print(f"  Network restrictions: {'✅ Active' if net_status else '❌ Inactive'}")
    # USB restriction status
    usb_status = is_usb_restricted(user)
    print(f"  USB restrictions: {'✅ Active' if usb_status else '❌ Inactive'}")

if __name__ == "__main__":
    main()
