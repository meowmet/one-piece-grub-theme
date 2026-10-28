
# One Piece GRUB Theme


![Preview](https://raw.githubusercontent.com/meowmet/one-piece-grub-theme/main/preview.gif)

A custom **One Piece themed GRUB bootloader** to spice up your system!

## ✅ Compatibility

| System | Status | Notes |
|---|---|---|
| **Fedora** | ✔ | `/boot/grub2`, BLS entries, `GRUB_TERMINAL_OUTPUT="console"` fixed automatically |
| **Ubuntu** | ✔ | Hidden menu is switched to visible |
| **Linux Mint** | ✔ | |
| **Debian** | ✔ | |
| **Arch Linux** | ✔ | Also Manjaro, EndeavourOS |
| **openSUSE** | ✔ | `/boot/grub2` |
| **Windows (dual-boot)** | ✔ | Detected with `os-prober`, shown with the Windows icon |
| Kali, Zorin, elementary, CentOS, Rocky | ✔ | |
| NixOS | ✔ | Installer prints the config snippet |
| Pop!_OS | ✘ | Uses systemd-boot by default, not GRUB |

Works with both **BIOS** and **UEFI** systems.

## 📦 Installation

```bash
git clone https://github.com/meowmet/one-piece-grub-theme.git
cd one-piece-grub-theme
sudo ./install.sh
```

The installer detects your distribution and:

* copies the theme to `/boot/grub/themes/one-piece` (or `/boot/grub2/themes/one-piece` on Fedora/openSUSE),
* sets `GRUB_THEME` in `/etc/default/grub` (a backup is saved next to it),
* enables the graphical terminal and a visible menu,
* enables `os-prober` so Windows shows up in the menu,
* regenerates `grub.cfg` with `update-grub`, `grub-mkconfig` or `grub2-mkconfig`.

### Choose a background

```bash
sudo ./install.sh --background zoro
```

Available: `luffy`, `monkey_d_luffy`, `zoro`, `goingmerry`, `sea`, `wanted`.

### Uninstall

```bash
sudo ./install.sh --uninstall
```

## 🪟 Windows dual-boot

GRUB 2.06+ disables `os-prober` by default; the installer turns it back on.
If Windows still does not appear:

1. Install os-prober:
   * Fedora: `sudo dnf install os-prober`
   * Ubuntu / Mint / Debian: `sudo apt install os-prober`
   * Arch / Manjaro: `sudo pacman -S os-prober`
   * openSUSE: `sudo zypper install os-prober`
2. Make sure the Windows EFI partition is mounted (UEFI) or the Windows partition is readable.
3. Disable Windows *Fast Startup* so its partition is not locked.
4. Run `sudo ./install.sh` again.

## 🛠️ Manual installation

```bash
# Debian / Ubuntu / Mint / Arch
sudo mkdir -p /boot/grub/themes/one-piece
sudo cp -r theme.txt *.pf2 background.png select_*.png terminal_box_*.png icons backgrounds /boot/grub/themes/one-piece/
# Fedora / openSUSE: use /boot/grub2/themes/one-piece instead
```

In `/etc/default/grub`:

```bash
GRUB_THEME="/boot/grub/themes/one-piece/theme.txt"   # /boot/grub2/... on Fedora/openSUSE
GRUB_DISABLE_OS_PROBER=false
#GRUB_TERMINAL_OUTPUT="console"                     # comment out on Fedora
```

Then update GRUB:

* Debian / Ubuntu / Mint / Kali: `sudo update-grub`
* Arch / EndeavourOS: `sudo grub-mkconfig -o /boot/grub/grub.cfg`
* Fedora / openSUSE: `sudo grub2-mkconfig -o /boot/grub2/grub.cfg`

On Fedora also run `sudo grub2-editenv - unset menu_auto_hide` so the menu is not hidden.

## ✨ Credits

Made by **Meowmet**

> *If you have any recommendations, please mention them.* 🙌


## 📝 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
