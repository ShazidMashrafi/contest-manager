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


def remove_all_iptables(user):
    """Remove all iptables rules and custom chains for the user."""
    try:
        uid = pwd.getpwnam(user).pw_uid
        chain_out = f"CONTEST_{user.upper()}_OUT"
        # Remove OUTPUT jump
        subprocess.run(['iptables', '-D', 'OUTPUT', '-m', 'owner', '--uid-owner', str(uid), '-j', chain_out], check=False)
        subprocess.run(['ip6tables', '-D', 'OUTPUT', '-m', 'owner', '--uid-owner', str(uid), '-j', chain_out], check=False)
        # Flush and delete custom chains
        subprocess.run(['iptables', '-F', chain_out], check=False)
        subprocess.run(['iptables', '-X', chain_out], check=False)
        subprocess.run(['ip6tables', '-F', chain_out], check=False)
        subprocess.run(['ip6tables', '-X', chain_out], check=False)
        # Remove any remaining REJECT rules
        subprocess.run(['iptables', '-D', 'OUTPUT', '-m', 'owner', '--uid-owner', str(uid), '-j', 'REJECT'], check=False)
        subprocess.run(['ip6tables', '-D', 'OUTPUT', '-m', 'owner', '--uid-owner', str(uid), '-j', 'REJECT'], check=False)
        print(f"✅ All iptables rules removed for user '{user}'")
    except Exception as e:
        print(f"⚠️  Failed to remove all iptables rules for user '{user}': {e}")


def main():
    """Main unrestrict CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    check_root()
    config_dir = args.config_dir or get_project_root()
    try:
        # Remove all iptables rules for the user
        remove_all_iptables(args.user)
        # Remove USB restrictions
        from ..utils.usb_restrictor import USBRestrictor
        usb_restrictor = USBRestrictor(args.user)
        usb_restrictor.remove_usb_restrictions()
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
