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
Run `contest-manager --help` for a full list of commands and options.

---

## Setup

Set up a contest user and environment:

```bash
sudo contest-manager setup [username]

# Example:
sudo contest-manager setup           # sets up 'participant'
sudo contest-manager setup contestant     # sets up 'contestant'
```

This command creates the user, installs all required packages, and configures the environment using files in `config/`.

---

## Restrict

Apply contest restrictions (network and USB) to a user:

```bash
sudo contest-manager restrict [username]

# Example:
sudo contest-manager restrict        # restricts 'participant'
sudo contest-manager restrict contestant  # restricts 'contestant'
```

This command blocks all domains listed in `config/blacklist.txt` and disables USB storage devices for the user.

---

## Unrestrict

Remove all contest restrictions from a user:

```bash
sudo contest-manager unrestrict [username]

# Example:
sudo contest-manager unrestrict      # removes from 'participant'
sudo contest-manager unrestrict contestant
```

This command removes all network and USB restrictions for the user.

---

## Reset

Reset a user's environment to a clean state:

```bash
sudo contest-manager reset [username]

# Example:
sudo contest-manager reset           # resets 'participant'
sudo contest-manager reset contestant
```

---

## Status

Check the current restriction and USB status for a user:

```bash
contest-manager status [username]

# Example:
contest-manager status               # checks 'participant'
contest-manager status contestant
```

---

## Config File Management

All user-editable configuration files are in the `config/` folder at the project root:

- `config/blacklist.txt`: List of domains to block for contest users.
- `config/apt.txt`: List of apt packages to install.
- `config/snap.txt`: List of snap packages to install.
- `config/flatpak.txt`: List of flatpak packages to install.

Edit these files as needed for your contest environment. No domains or packages are hardcoded; all are file-driven.

---