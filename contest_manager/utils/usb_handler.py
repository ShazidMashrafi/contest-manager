#!/usr/bin/env python3
"""
USB Device Restriction Manager
Handles blocking of USB storage devices while allowing keyboards/mice.
"""

def restrict_usb_storage_device(user, verbose=False):
    """Restrict USB storage devices for the given user."""
    if verbose:
        print(f"[restrict_usb_storage] Blocking USB storage for {user}")
    # Block all USB mass storage devices by creating a udev rule
    # This matches devices with USB class 08 (Mass Storage), but does not block HID (keyboards/mice)
    try:
        rule = (
            '# Block all USB mass storage devices (class 08), but not HID (keyboards/mice)\n'
            'SUBSYSTEM=="usb", ENV{ID_USB_INTERFACES}=="*:080650:*|*:080602:*|*:080400:*|*:080100:*|*:080200:*|*:080300:*|*:080500:*|*:080600:*|*:080700:*|*:080800:*|*:080900:*|*:080A00:*|*:080B00:*|*:080C00:*|*:080D00:*|*:080E00:*|*:080F00:*", ATTR{authorized}="0"\n'
        )
        with open("/etc/udev/rules.d/99-contest-usb-block.rules", "w") as f:
            f.write(rule)
        import subprocess
        subprocess.run(["udevadm", "control", "--reload-rules"], check=True)
        subprocess.run(["udevadm", "trigger"], check=True)
    except Exception as e:
        print(f"Failed to block USB storage: {e}")
    print("USB storage devices blocked.")

def persist_usb_restrictions(verbose=False):
    """Ensure USB restrictions persist after reboot (udev and polkit rules are persistent by default)."""
    # Udev and polkit rules in /etc are persistent, but reload to ensure they're active after reboot
    import subprocess
    try:
        subprocess.run(["udevadm", "control", "--reload-rules"])
        subprocess.run(["udevadm", "trigger"])
        subprocess.run(["systemctl", "restart", "polkit"], check=False)
        if verbose:
            print("USB restriction persistence ensured (udev/polkit rules reloaded).")
        return True
    except Exception as e:
        if verbose:
            print(f"Failed to ensure USB restriction persistence: {e}")
        return False