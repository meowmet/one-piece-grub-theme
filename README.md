---

# one-piece-grub-theme 🏴‍☠️

A **One Piece-themed GRUB bootloader menu** featuring custom wallpapers, fonts, and icons. Transform your Linux boot screen into a Straw Hat adventure!

---

## Preview

![Preview]([preview.png](https://github.com/meowmet/one-piece-grub-theme/blob/main/background.png))

One piece themed wallpapers : `luffy.png`, `zoro.jpg`, `goingmerry.jpg`, `wanted.jpg`, `sea.jpg`, and more.

---


## Installation



1. **Copy theme files** to your GRUB themes folder:

   ```bash
   sudo mkdir -p /boot/grub/themes/one-piece-grub-theme
   sudo cp -r /path/to/your/theme/* /boot/grub/themes/one-piece-grub-theme/
   ```

2. **Edit GRUB default configuration**:

   ```bash
   sudo nano /etc/default/grub
   ```

   * Add or edit the line to set the theme:

     ```text
     GRUB_THEME="/boot/grub/themes/one-piece-grub-theme/theme.txt"
     ```

   * Optional: adjust timeout and default OS:

     ```text
     GRUB_TIMEOUT=10
     GRUB_DEFAULT=0
     ```

3. **Update GRUB** to apply changes:

   ```bash
   sudo update-grub      # Debian/Ubuntu
   # or
   sudo grub-mkconfig -o /boot/grub/grub.cfg   # Arch/others
   ```

4. **Reboot** and enjoy your One Piece GRUB menu!

---

## Customization

You can tweak `theme.txt` to adjust:

* Terminal box position, size, and font (`terminal-box`, `terminal-font`)
* Boot menu item colors and fonts (`boot_menu`)
* Timeout labels (`label`)
* Background image (`desktop-image`)

Ensure your images and fonts are correctly placed in the theme folder.

---

## Included Files

```
background.png
onepiece.pf2
theme.txt
terminal_box_*.png
select_*.png
icons/*.png
backgrounds/*.jpg
```



## License

MIT License – feel free to use, modify, and share.

---

This README provides clear installation steps, customization options, and credits, ensuring users can easily set up and personalize your One Piece GRUB theme.
