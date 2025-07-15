
# Contest Environment Manager

A robust, modular system for setting up a PC for onsite competitive programming contests, with intuitive configuration via editable files in the `config/` folder.

---

git clone <github.com/shazidmashrafi/contest-manager>
sudo ./install.sh
sudo contest-manager setup --user contestant
sudo contest-manager restrict --user contestant
contest-manager status --user contestant
sudo contest-manager unrestrict --user contestant

## 🚀 Quick Start

```sh
git clone <github.com/shazidmashrafi/contest-manager>
cd contest-manager
sudo bash install.sh
sudo contest-manager setup --user contestant
```

See [Usage Guide](USAGE.md) for all commands and details.

---


## ✨ Features
- **Network Restrictions:** Block access to blacklisted sites (see `config/blacklist.txt`)
- **USB Controls:** Block USB storage devices
- **Easy CLI:** One command for setup, restrict, unrestrict, reset, and status
- **Persistent & Secure:** Survives reboot, systemd integration
- **Intuitive Config:** All user-editable lists (blacklist, package lists) are in the `config/` folder

---


## 📚 Documentation
- [Install Guide](docs/INSTALL.md)
- [Usage Guide](docs/USAGE.md)
- [Config File Reference](config/README_config.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

---

## 🛠️ Requirements
- Ubuntu 18.04+ (or compatible Linux)
- Python 3.6+
- Root privileges for install/restriction

---

## 🏆 Use Cases
- Programming contests (ICPC, IUPC, NCPC & onsite programming contests)

---

**Built with ❤️ for secure, fair contests.**
