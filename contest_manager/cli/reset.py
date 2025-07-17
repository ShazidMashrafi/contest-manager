#!/usr/bin/env python3
"""
Contest Environment Reset CLI
"""

import sys
import argparse
from contest_manager.utils.utils import check_root
from contest_manager.utils.user_manager import reset_user_account

def main():
    parser = argparse.ArgumentParser(
        description="Reset user account to clean state",
        prog="contest-reset"
    )
    parser.add_argument(
        'user',
        nargs='?',
        default='participant',
        help='Username to reset (default: participant)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    args = parser.parse_args()

    check_root()

    try:
        success = reset_user_account(args.user)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nReset cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Reset error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
