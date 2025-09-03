
# One Piece GRUB Theme


![Preview](https://raw.githubusercontent.com/meowmet/one-piece-grub-theme/main/preview.gif)

A custom **One Piece themed GRUB bootloader** to spice up your system!



## 📦 Installation

1. **Clone this repo**
   ```bash
   git clone https://github.com/meowmet/one-piece-grub-theme.git
   cd one-piece-grub-theme


2. **Copy theme folder** to GRUB themes directory:

   ```bash
   sudo mkdir -p /boot/grub/themes
   sudo cp -r one-piece /boot/grub/themes/
   ```

3. **Edit GRUB config**
   Open `/etc/default/grub` with your favorite editor and add/change this line:

   ```bash
   GRUB_THEME="/boot/grub/themes/one-piece/theme.txt"
   ```

4. **Update GRUB**
   On Debian/Ubuntu/Kali:

   ```bash
   sudo update-grub
   ```

   On Fedora/Arch:

   ```bash
   sudo grub-mkconfig -o /boot/grub/grub.cfg
   ```

5. **Reboot and enjoy** 

---

## 🛠️ Extra Notes

* Works with both **BIOS** and **UEFI** systems.
* If you don’t see the theme, double-check the theme path in `/etc/default/grub`.
* Background, fonts, and icons can be customized inside the theme folder.

---

## ✨ Credits

Made by **Meowmet** 

> *If you have any recommendations, please mention them.* 🙌


📝 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
