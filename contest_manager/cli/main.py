#!/usr/bin/env python3
"""
Contest Environment Manager - Main CLI Entry Point
"""

import sys
import argparse
from contest_manager.utils.utils import check_root
from contest_manager.cli.setup import main as setup_main
from contest_manager.cli.reset import main as reset_main
from contest_manager.cli.restrict import main as restrict_main
from contest_manager.cli.unrestrict import main as unrestrict_main
from contest_manager.cli.status import main as status_main

def main():
    parser = argparse.ArgumentParser(
        description="Contest Environment Manager",
        prog="contest-manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo contest-manager setup                   # Set up lab PC for users in /config/users.txt
  sudo contest-manager restrict                # Restrict default user (participant)
  sudo contest-manager unrestrict              # Remove restrictions for participant
  sudo contest-manager reset                   # Reset participant account to clean state
  sudo contest-manager status                  # Check status for participant
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    setup_parser = subparsers.add_parser('setup', help='Set up lab PC with all required software')
    setup_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')

    reset_parser = subparsers.add_parser('reset', help='Reset user account to clean state')
    reset_parser.add_argument('user', nargs='?', default='participant', help='Username (default: participant)')
    reset_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')

    restrict_parser = subparsers.add_parser('restrict', help='Enable internet restrictions')
    restrict_parser.add_argument('user', nargs='?', default='participant', help='Username (default: participant)')
    restrict_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')

    unrestrict_parser = subparsers.add_parser('unrestrict', help='Disable internet restrictions')
    unrestrict_parser.add_argument('user', nargs='?', default='participant', help='Username (default: participant)')
    unrestrict_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')

    status_parser = subparsers.add_parser('status', help='Show current restriction status')
    status_parser.add_argument('user', nargs='?', default='participant', help='Username (default: participant)')
    status_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')


    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        check_root()
        if args.command == "setup":
            sys.argv = [sys.argv[0]] + (['--verbose'] if args.verbose else [])
            setup_main()
        elif args.command == "reset":
            sys.argv = [sys.argv[0]] + [args.user] + (['--verbose'] if args.verbose else [])
            reset_main()
        elif args.command == "restrict":
            sys.argv = [sys.argv[0]] + [args.user] + (['--verbose'] if args.verbose else [])
            restrict_main()
        elif args.command == "unrestrict":
            sys.argv = [sys.argv[0]] + [args.user] + (['--verbose'] if args.verbose else [])
            unrestrict_main()
        elif args.command == "status":
            sys.argv = [sys.argv[0]] + [args.user] + (['--verbose'] if args.verbose else [])
            status_main()
        else:
            parser.print_help()
            sys.exit(1)
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
