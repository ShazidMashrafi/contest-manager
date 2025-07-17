#!/usr/bin/env python3
"""
User management utilities for contest environment.
"""

import os
import subprocess
from pathlib import Path
import pwd
import shutil
from .utils import *

def create_user_backup(user):
    """Create backup of user's home directory."""
    print(f"→ Creating backup of user '{user}' home directory...")
    
    backup_dir = f"/opt/{user}_backup"
    user_home = f"/home/{user}"
    backup_home = f"{backup_dir}/{user}_home"
    
    # Create backup directory
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create backup if it doesn't exist
    if not os.path.exists(backup_home):
        run_command(f"rsync -aAX {user_home}/ {backup_home}/", shell=True)
        print(f"✅ Backup created at {backup_home}")
    else:
        print("✅ Backup already exists. Skipping.")

def set_user_permissions(user):
    """Set ownership, permissions, and umask for user home."""
    user_home = f"/home/{user}"
    if not os.path.exists(user_home):
        print(f"❌ Home directory does not exist for user: {user}")
        return
    subprocess.run(f"chown -R {user}:{user} {user_home}", shell=True)
    subprocess.run(f"chmod -R u+rwX,go-w {user_home}", shell=True)
    # Set umask for future files
    umask_line = "umask 022"
    for file_path in [f"{user_home}/.bashrc", f"{user_home}/.profile"]:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            if umask_line not in content:
                with open(file_path, 'a') as f:
                    f.write(f"\n{umask_line}\n")
        except FileNotFoundError:
            with open(file_path, 'w') as f:
                f.write(f"{umask_line}\n")
    print(f"✅ Permissions and umask set for {user}")
        
def remove_from_privileged_groups(user):
    """Remove user from privileged groups."""
    privileged_groups = ["sudo", "netdev", "adm", "disk"]
    for group in privileged_groups:
        run_command(f"gpasswd -d {user} {group}", shell=True, check=False)


def user_exists(username):
    """Check if a user exists."""
    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        return False

def delete_user(username):
    """Delete a user and their home directory."""
    print(f"→ User '{username}' exists. Deleting...")
    subprocess.run(f"deluser {username} --remove-home", shell=True, check=False)
    print(f"✅ User '{username}' deleted successfully.")

def create_user(username, password):
    """Create a contest user with minimal privileges and setup."""
    if user_exists(username):
        delete_user(username)
    subprocess.run(f"useradd -m -s /bin/bash {username} -G audio,video,cdrom,plugdev,users", shell=True)
    if password:
        subprocess.run(f"echo '{username}:{password}' | chpasswd", shell=True)
    else:
        subprocess.run(f"passwd -d {username}", shell=True)
    subprocess.run(f"usermod -U {username}", shell=True)
    remove_from_privileged_groups(username)
    set_user_permissions(username)
    create_user_backup(username)
    print(f"✅ User '{username}' created successfully with minimal privileges and correct permissions.")

        
def extract_user_password_pairs(file_path):
    """Extract user/password pairs from file."""
    pairs = []
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split()
                username = parts[0]
                password = parts[1] if len(parts) > 1 else ""
                pairs.append((username, password))
    if not pairs:
        print("❌ No users found in users file")
    return pairs

def check_file_exists(file_path):
    """Check if the given file exists."""
    exists = Path(file_path).exists()
    if not exists:
        print(f"❌ File not found: {file_path}")
    return exists
    
def setup_users(users_file_path):
    """
    Extracts user/password pairs, and sets up each user.
    Handles both password and empty password cases.
    """
    if not check_file_exists(users_file_path):
        return False
    pairs = extract_user_password_pairs(users_file_path)
    if not pairs:
        return False
    for username, password in pairs:
        print(f"→ Setting up user account '{username}'")
        create_user(username, password)
    return True


def backup_exists(user):
    backup_home = f"/opt/{user}_backup/{user}_home"
    return os.path.exists(backup_home)

def is_user_logged_in(user):
    try:
        result = subprocess.run(['pgrep', '-u', user], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def delete_home_contents(user):
    user_home = f"/home/{user}"
    print(f"→ Deleting contents of {user_home}...")
    home_path = Path(user_home)
    if home_path.exists():
        for item in home_path.iterdir():
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

def restore_home_from_backup(user):
    backup_home = f"/opt/{user}_backup/{user}_home"
    user_home = f"/home/{user}"
    print(f"→ Restoring from {backup_home}...")
    cmd = f"rsync -aAX {backup_home}/ {user_home}/"
    result = run_command(cmd, shell=True, check=False, capture_output=True)
    if result.returncode != 0:
        print(f"❌ Failed to restore backup: {result.stderr}")
        return False
    return True

def reset_user_account(user):
    """Reset a user account to clean state by restoring from backup."""
    print(f"→ Resetting user account '{user}'")
    if not user_exists(user):
        print(f"❌ User '{user}' does not exist")
        return False
    if not backup_exists(user):
        print(f"❌ Backup directory /opt/{user}_backup/{user}_home does not exist")
        print("Please run setup first to create a backup")
        return False
    if is_user_logged_in(user):
        print(f"❌ User '{user}' is currently logged in")
        print("Please log them out before resetting")
        return False
    try:
        delete_home_contents(user)
        if not restore_home_from_backup(user):
            return False
        set_user_permissions(user)
        print(f"✅ User '{user}' reset successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to reset user account: {e}")
        return False