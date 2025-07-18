# Usage Guide - Contest Environment Manager

This guide explains how to use the Contest Environment Manager CLI to set up, restrict, unrestrict, reset, and check the status of contest user environments.

## Table of Contents

- [Install](#install)
- [Setup Environment](#setup)
- [Restrict](#restrict)
- [Unrestrict](#unrestrict)
- [Reset](#reset)
- [Status](#status)
- [Start](#start)
- [Update](#update)

---

## Install

To install the Contest Environment Manager CLI, run:

```bash
sudo bash install.sh
```

You can also specify a custom base command:

```bash
sudo bash install.sh mdpc
```

If no argument is given, it defaults to `contest-manager`.


## Setup environment

To set up the contest environment, run:

```bash
sudo contest-manager setup
```

This command will:
- Create all users listed in `config/users.txt`
- Install packages from `config/apt.txt`, `config/snap.txt`, and `config/flatpak.txt`
- Install VS Code extensions from `config/vscode-extensions.txt`
- Apply system settings for the contest

### How to use the config files

**config/users.txt**
  - Format: `username password` (password optional)
  - Example:
    ```
    contestant 123
    participant
    ```
  - Lines starting with `#` are comments and ignored.

**config/apt.txt**
  - List of apt packages to install, one per line.
  - You can add PPAs using lines like: `package(ppa:ppa-link)`
  - Example:
    ```
    build-essential
    gcc
    firefox
    grub-customizer(ppa:danielrichter2007/grub-customizer)
    ```

**config/snap.txt**
  - List of snap packages to install, one per line, as you would use with `snap install`.
  - Example:
    ```
    code --classic
    sublime-text --classic
    ```

**config/flatpak.txt**
  - List of flatpak packages to install, one per line, as you would use with `flatpak install -y`.
  - Example:
    ```
    flathub org.vscode.Code
    ```

**config/vscode-extensions.txt**
  - List of VS Code extensions to install, one per line.
  - Example:
    ```
    ms-vscode.cpptools
    ms-python.python
    redhat.java
    ```

Edit these files as needed before running the setup command. All configuration is file-driven; no arguments are required.

## Restrict

To restrict a contest user's environment (block internet and USB storage):

```bash
sudo contest-manager restrict [username]
```

- If no username is given, it defaults to `participant`.
- Restrictions are applied using the blacklist in `config/blacklist.txt`.
- USB storage devices are blocked for the user.
- Restrictions are persisted until manually removed by unrestrict command.

**Example:**
```bash
sudo contest-manager restrict
sudo contest-manager restrict contestant
```

## Unrestrict

To remove all contest restrictions (restore internet and USB access) for a user:

```bash
sudo contest-manager unrestrict [username]
```

- If no username is given, it defaults to `participant`.
- Removes internet restrictions using `config/blacklist.txt`.
- Restores USB storage device access for the user.

**Example:**
```bash
sudo contest-manager unrestrict
sudo contest-manager unrestrict contestant
```
## Status

To check the current restriction status for a user:

```bash
sudo contest-manager status [username]
```

- If no username is given, it defaults to `participant`.
- Shows whether internet and USB restrictions are active for the user.

**Example:**
```bash
sudo contest-manager status
sudo contest-manager status contestant
```

## Reset

To reset a contest user's environment to a clean state (restore home from backup):

```bash
sudo contest-manager reset [username]
```

- If no username is given, it defaults to `participant`.
- Restores the user's home directory from backup.
- Removes any changes made during the contest session.

**Example:**
```bash
sudo contest-manager reset
sudo contest-manager reset contestant
```

---

## Start

To start the restriction system at boot (for persistence):

```bash
sudo contest-manager start
```

- This command is automatically used by the contest-manager system (e.g., via systemd/cron) to ensure restrictions persist after reboot.
- You can also run it manually if needed.

**Example:**
```bash
sudo contest-manager start
```

---

## Update

To update internet restrictions (refresh iptables rules):

```bash
sudo contest-manager update
```

- This command is automatically used by the contest-manager system (e.g., via systemd/cron) to keep internet restrictions up to date as IPs change.
- You can also run it manually if needed.

**Example:**
```bash
sudo contest-manager update
```

---

# Need Help?

For troubleshooting, advanced configuration, or more details, see the project README or run:

```bash
$BASE_CMD --help
```

For bug reports or feature requests, please contact the maintainer or open an issue on GitHub.

---

Thank you for using the Contest Environment Manager!

