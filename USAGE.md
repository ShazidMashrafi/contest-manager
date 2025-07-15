# Usage Guide - Contest Environment Manager

This guide explains how to use the Contest Environment Manager CLI to set up, restrict, unrestrict, reset, and check the status of contest user environments.

## Table of Contents

- [Overview](#overview)
- [Setup](#setup)
- [Restrict](#restrict)
- [Unrestrict](#unrestrict)
- [Reset](#reset)
- [Status](#status)
- [Config File Management](#config-file-management)

---

## Overview

All commands default to the user `participant` if no username is provided.  

By default, the CLI command is `contest-manager`. You can customize the base command by running:

```bash
sudo bash install.sh mdpc
```

This will use `mdpc` as the base command for all CLI operations. If no argument is given, it defaults to `contest-manager`.

Run `$BASE_CMD --help` for a full list of commands and options (replace `$BASE_CMD` with your chosen command).

---

## Setup

Set up a contest user and environment:

```bash
sudo contest-manager setup [username]

# Example:
sudo contest-manager setup           # sets up 'participant'
sudo contest-manager setup contestant     # sets up 'contestant'

```bash
# Default:

# Custom:
Apply contest restrictions (network and USB) to a user:

# Example:

```bash
sudo contest-manager restrict [username]
```

# Example:
sudo contest-manager restrict        # restricts 'participant'
sudo contest-manager restrict contestant  # restricts 'contestant'

```bash
# Default:

# Custom:
Remove all contest restrictions from a user:

# Example:

```bash
sudo contest-manager unrestrict [username]
```

# Example:
sudo contest-manager unrestrict      # removes from 'participant'
sudo contest-manager unrestrict contestant

```bash
# Default:

# Custom:
Reset a user's environment to a clean state:

# Example:

```bash
sudo contest-manager reset [username]
```

# Example:
sudo contest-manager reset           # resets 'participant'
sudo contest-manager reset contestant

```bash
# Default:

# Custom:
```bash

# Example:
contest-manager status [username]

# Example:
```
contest-manager status               # checks 'participant'
contest-manager status contestant

```bash
# Default:

# Custom:
- `config/blacklist.txt`: List of domains to block for contest users.

# Example:
- `config/apt.txt`: List of apt packages to install.
- `config/snap.txt`: List of snap packages to install.
- `config/flatpak.txt`: List of flatpak packages to install.
```

Edit these files as needed for your contest environment. No domains or packages are hardcoded; all are file-driven.

---