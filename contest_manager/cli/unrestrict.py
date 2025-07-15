#!/usr/bin/env python3
"""
Contest Environment Unrestrict CLI
"""

import sys
import argparse
import subprocess
import pwd
from ..utils.common import check_root, get_project_root


def create_parser():
    """Create the unrestrict argument parser."""
    parser = argparse.ArgumentParser(
        description="Disable all internet and USB restrictions for contest environment",
        prog="contest-unrestrict"
    )
    parser.add_argument(
        'user',
        nargs='?',
        default='participant',
        help='Username to unrestrict (default: participant)'
    )
    parser.add_argument(
        '--config-dir',
        type=str,
        help='Configuration directory path (default: project root)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    return parser



from ..utils.blacklist_restrictor import remove_all_blacklist_iptables


def main():
    """Main unrestrict CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    check_root()
    config_dir = args.config_dir or get_project_root()
    try:
        # Remove all blacklist-based network restrictions
        remove_all_blacklist_iptables(args.user)
        # Remove USB storage restrictions
        from ..utils.usb_restrictor import remove_usb_restrictions
        remove_usb_restrictions(args.user)
        print(f"Restrictions removed for user '{args.user}'.")
        sys.exit(0)
    except KeyboardInterrupt:
        print("\nUnrestriction cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unrestriction error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
