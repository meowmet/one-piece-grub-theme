#!/usr/bin/env bash
# One Piece GRUB theme installer.
# Supports Fedora, Ubuntu, Linux Mint, Debian, Arch (and derivatives such as
# Manjaro, EndeavourOS, Kali, Zorin, openSUSE) and dual-boot with Windows.
#
# Usage:
#   sudo ./install.sh                      install with the default background
#   sudo ./install.sh --background zoro    use backgrounds/zoro.png instead
#   sudo ./install.sh --uninstall          remove the theme
set -euo pipefail

THEME_NAME="one-piece"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GRUB_DEFAULT_CFG="/etc/default/grub"

info()  { printf '\033[1;33m[*]\033[0m %s\n' "$*"; }
ok()    { printf '\033[1;32m[+]\033[0m %s\n' "$*"; }
warn()  { printf '\033[1;31m[!]\033[0m %s\n' "$*"; }
die()   { warn "$*"; exit 1; }

usage() {
    sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'
    echo "Available backgrounds:"
    for f in "$SRC_DIR"/backgrounds/*.png; do echo "  $(basename "$f" .png)"; done
}

BACKGROUND=""
UNINSTALL=0
while [ $# -gt 0 ]; do
    case "$1" in
        -b|--background) BACKGROUND="${2:-}"; shift 2 ;;
        -u|--uninstall)  UNINSTALL=1; shift ;;
        -h|--help)       usage; exit 0 ;;
        *) usage; die "Unknown option: $1" ;;
    esac
done

[ "$(id -u)" -eq 0 ] || die "Please run as root: sudo $0 $*"

# --- Detect distribution ----------------------------------------------------
DISTRO_ID="unknown"
DISTRO_LIKE=""
if [ -r /etc/os-release ]; then
    . /etc/os-release
    DISTRO_ID="${ID:-unknown}"
    DISTRO_LIKE="${ID_LIKE:-}"
fi
info "Detected distribution: ${PRETTY_NAME:-$DISTRO_ID}"

if [ "$DISTRO_ID" = "nixos" ]; then
    cat <<EOF
NixOS manages GRUB declaratively. Copy this folder somewhere in your config
and add to configuration.nix:

  boot.loader.grub.theme = ./one-piece-grub-theme;
  boot.loader.grub.useOSProber = true;   # detect Windows

then run: sudo nixos-rebuild switch
EOF
    exit 0
fi

# --- Detect GRUB layout -----------------------------------------------------
# Fedora / RHEL / openSUSE use "grub2-*" tools and /boot/grub2,
# Debian / Ubuntu / Mint / Arch use "grub-*" tools and /boot/grub.
if command -v grub2-mkconfig >/dev/null 2>&1 && [ -d /boot/grub2 ]; then
    GRUB_DIR="/boot/grub2"
    MKCONFIG="grub2-mkconfig"
elif command -v grub-mkconfig >/dev/null 2>&1; then
    GRUB_DIR="/boot/grub"
    MKCONFIG="grub-mkconfig"
else
    die "GRUB was not found. This system probably uses another bootloader
    (e.g. Pop!_OS uses systemd-boot). Install GRUB first."
fi
[ -f "$GRUB_DEFAULT_CFG" ] || die "$GRUB_DEFAULT_CFG not found."

THEME_DIR="$GRUB_DIR/themes/$THEME_NAME"

update_grub_cfg() {
    info "Regenerating GRUB configuration..."
    if command -v update-grub >/dev/null 2>&1; then
        update-grub
    else
        "$MKCONFIG" -o "$GRUB_DIR/grub.cfg"
    fi
    # Older Fedora/RHEL UEFI installs read a full grub.cfg from the ESP
    # instead of a stub that points to $GRUB_DIR/grub.cfg.
    local efi_cfg="/boot/efi/EFI/$DISTRO_ID/grub.cfg"
    if [ -f "$efi_cfg" ] && ! grep -q "configfile" "$efi_cfg"; then
        "$MKCONFIG" -o "$efi_cfg"
    fi
}

backup_default_cfg() {
    local backup="$GRUB_DEFAULT_CFG.bak.$(date +%Y%m%d%H%M%S)"
    cp -a "$GRUB_DEFAULT_CFG" "$backup"
    ok "Backup of $GRUB_DEFAULT_CFG saved to $backup"
}

# set_var KEY VALUE: replace an active KEY= line, or append one.
set_var() {
    if grep -qE "^[[:space:]]*$1=" "$GRUB_DEFAULT_CFG"; then
        sed -i -E "s|^[[:space:]]*$1=.*|$1=\"$2\"|" "$GRUB_DEFAULT_CFG"
    else
        echo "$1=\"$2\"" >> "$GRUB_DEFAULT_CFG"
    fi
}

get_var() {
    grep -E "^[[:space:]]*$1=" "$GRUB_DEFAULT_CFG" | tail -n1 | cut -d= -f2- | tr -d "\"'" || true
}

comment_var() {
    sed -i -E "s|^[[:space:]]*($1=.*)|#\1|" "$GRUB_DEFAULT_CFG"
}

# --- Uninstall --------------------------------------------------------------
if [ "$UNINSTALL" -eq 1 ]; then
    backup_default_cfg
    comment_var GRUB_THEME
    rm -rf "$THEME_DIR"
    update_grub_cfg
    ok "Theme removed."
    exit 0
fi

# --- Copy theme files -------------------------------------------------------
info "Installing theme to $THEME_DIR"
rm -rf "$THEME_DIR"
mkdir -p "$THEME_DIR"
cp -a "$SRC_DIR"/theme.txt "$SRC_DIR"/*.pf2 "$SRC_DIR"/background.png \
      "$SRC_DIR"/select_*.png "$SRC_DIR"/terminal_box_*.png \
      "$SRC_DIR"/icons "$SRC_DIR"/backgrounds "$THEME_DIR"/

if [ -n "$BACKGROUND" ]; then
    bg="$SRC_DIR/backgrounds/$BACKGROUND.png"
    [ -f "$bg" ] || { usage; die "Background '$BACKGROUND' not found."; }
    cp -a "$bg" "$THEME_DIR/background.png"
    ok "Background set to $BACKGROUND"
fi

# --- Configure /etc/default/grub --------------------------------------------
backup_default_cfg
set_var GRUB_THEME "$THEME_DIR/theme.txt"

# Themes need the graphical terminal. Fedora ships GRUB_TERMINAL_OUTPUT="console".
for var in GRUB_TERMINAL GRUB_TERMINAL_OUTPUT; do
    if [ "$(get_var $var)" = "console" ]; then
        comment_var "$var"
        ok "Disabled $var=console (required for graphical themes)"
    fi
done

[ -n "$(get_var GRUB_GFXMODE)" ] || set_var GRUB_GFXMODE "1920x1080,auto"

# Show the menu instead of hiding it (Ubuntu/Fedora hide it on single-OS systems).
if [ "$(get_var GRUB_TIMEOUT_STYLE)" = "hidden" ]; then
    set_var GRUB_TIMEOUT_STYLE "menu"
fi
timeout="$(get_var GRUB_TIMEOUT)"
if [ -z "$timeout" ] || [ "$timeout" = "0" ]; then
    set_var GRUB_TIMEOUT "10"
fi
if command -v grub2-editenv >/dev/null 2>&1; then
    grub2-editenv - unset menu_auto_hide 2>/dev/null || true
fi

# Windows dual-boot: GRUB >= 2.06 disables os-prober by default.
set_var GRUB_DISABLE_OS_PROBER "false"
if ! command -v os-prober >/dev/null 2>&1; then
    warn "os-prober is not installed, so Windows will not appear in the menu."
    case " $DISTRO_ID $DISTRO_LIKE " in
        *" fedora "*|*" rhel "*)  warn "Install it with: sudo dnf install os-prober" ;;
        *" debian "*|*" ubuntu "*) warn "Install it with: sudo apt install os-prober" ;;
        *" arch "*)               warn "Install it with: sudo pacman -S os-prober" ;;
        *" suse "*|*" opensuse "*) warn "Install it with: sudo zypper install os-prober" ;;
    esac
    warn "Then re-run this script."
fi

update_grub_cfg
ok "One Piece GRUB theme installed. Reboot and set sail!"
