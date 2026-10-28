#!/usr/bin/env bash
# Boot a theme in real GRUB inside QEMU and save a screenshot.
# Needs: grub-mkrescue (grub-pc-bin), xorriso, mtools, qemu-system-x86, imagemagick
#
#   tools/grub-screenshot.sh zoro [out.png] [WIDTHxHEIGHT]
set -euo pipefail

THEME="${1:?usage: $0 <theme> [out.png] [resolution]}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$(realpath -m "${2:-$REPO/previews/$THEME.jpg}")"
MODE="${3:-1920x1080}"
WORK="$(mktemp -d)"
trap 'kill "${QEMU_PID:-0}" 2>/dev/null || true; rm -rf "$WORK"' EXIT

mkdir -p "$WORK/iso/boot/grub/themes"
"$REPO/setup" build "$THEME" "$WORK/iso/boot/grub/themes/one-piece" >/dev/null

{
    cat <<EOF
insmod all_video
insmod gfxterm
insmod png
set gfxmode=$MODE
set gfxpayload=keep
terminal_output gfxterm
EOF
    for f in "$WORK"/iso/boot/grub/themes/one-piece/*.pf2; do
        echo "loadfont /boot/grub/themes/one-piece/$(basename "$f")"
    done
    cat <<'EOF'
set theme=/boot/grub/themes/one-piece/theme.txt
set timeout=60
menuentry 'Fedora Linux (6.11.4-301.fc41.x86_64) 41 (Workstation Edition)' --class fedora { true; }
menuentry 'Ubuntu' --class ubuntu --class gnu-linux --class gnu --class os { true; }
menuentry 'Windows Boot Manager (on /dev/nvme0n1p1)' --class windows --class os { true; }
submenu 'Advanced options for Ubuntu' { true; }
menuentry 'Memory test (memtest86+x64.efi)' --class memtest { true; }
menuentry 'UEFI Firmware Settings' --class efi { true; }
EOF
} > "$WORK/iso/boot/grub/grub.cfg"

grub-mkrescue -o "$WORK/theme.iso" "$WORK/iso" >/dev/null 2>&1
qemu-system-x86_64 -m 512 -cdrom "$WORK/theme.iso" -vga std -display none \
    -monitor "unix:$WORK/mon,server,nowait" &
QEMU_PID=$!
sleep "${WAIT:-12}"
python3 - "$WORK/mon" "$WORK/shot.ppm" <<'EOF'
import socket, sys, time
s = socket.socket(socket.AF_UNIX)
s.connect(sys.argv[1])
s.sendall(("screendump %s\n" % sys.argv[2]).encode())
time.sleep(2)
EOF
mkdir -p "$(dirname "$OUT")"
convert "$WORK/shot.ppm" "$OUT"
echo "$OUT"
