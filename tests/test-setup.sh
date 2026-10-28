#!/usr/bin/env bash
# Run ./setup against fake Fedora, Kali and Ubuntu systems in a temp dir.
#
#   tests/test-setup.sh
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
FAIL=0

check() {
    if [ "$2" = "$3" ]; then
        printf '  ok    %s\n' "$1"
    else
        printf '  FAIL  %s: expected "%s", got "%s"\n' "$1" "$3" "$2"
        FAIL=1
    fi
}

# make_system NAME MKCONFIG OS_RELEASE: fake root with stub tools.
make_system() {
    local root="$TMP/$1"
    mkdir -p "$root/bin" "$root/etc/default" "$root/boot/grub" "$root/boot/grub2" "$root/share" "$root/usr/bin"
    printf '%s\n' "$3" > "$root/os-release"
    # stub mkconfig: records that it ran; mentions grub.d only when asked to
    # shellcheck disable=SC2016
    printf '#!/bin/sh\n# %s\necho "$0 $*" >> %s/mkconfig.log\n' "$4" "$root" > "$root/bin/$2"
    for tool in grub2-editenv dnf apt-get; do
        printf '#!/bin/sh\necho "%s $*" >> %s/pkg.log\n' "$tool" "$root" > "$root/bin/$tool"
    done
    chmod +x "$root/bin/"*
    sed -e "s|/etc/default/grub|$root/etc/default/grub|g" \
        -e "s|/etc/os-release|$root/os-release|g" \
        -e "s|/boot/grub2|$root/boot/grub2|g; s|GRUB_DIR=\"/boot/grub\"|GRUB_DIR=\"$root/boot/grub\"|" \
        -e "s|\"/boot/efi\" |\"$root/efi\" |; s|for esp in /boot/efi /efi /boot|for esp in $root/efi|" \
        -e "s|lsblk -no FSTYPE|echo|" \
        -e "s|^SHARE_DIR=.*|SHARE_DIR=$root/share/op|; s|^GLOBAL_CMD=.*|GLOBAL_CMD=$root/usr/bin/onepiece-setup|" \
        -e "s|id -u|echo 0|" -e "s|/sys/class/drm|$root/drm|" -e "s|command -v os-prober|command -v os-prober-stub|g" \
        "$REPO/setup" > "$REPO/.setup-test-$1"
    chmod +x "$REPO/.setup-test-$1"
    echo "$root"
}

run() {
    local name="$1"; shift
    PATH="$TMP/$name/bin:/usr/bin:/bin" "$REPO/.setup-test-$name" "$@" < /dev/null > "$TMP/$name/out.log" 2>&1
}

# Effective value of a variable the way grub-mkconfig sees it.
effective() {
    local root="$TMP/$1"
    (
        set +u
        # shellcheck disable=SC1090,SC1091
        . "$root/etc/default/grub"
        for f in "$root"/etc/default/grub.d/*.cfg; do
            # shellcheck disable=SC1090
            [ -f "$f" ] && . "$f"
        done
        eval "echo \"\${$2}\""
    )
}

trap 'rm -rf "$TMP" "$REPO"/.setup-test-*' EXIT

echo "Fedora (grub2, console terminal, Windows on the ESP)"
root="$(make_system fedora grub2-mkconfig 'ID=fedora
PRETTY_NAME="Fedora Linux 41"' "")"
mkdir -p "$root/efi/EFI/Microsoft" "$root/drm/card0-HDMI-A-1"
echo connected > "$root/drm/card0-HDMI-A-1/status"
echo 2560x1440 > "$root/drm/card0-HDMI-A-1/modes"
cat > "$root/etc/default/grub" <<'EOF'
GRUB_TIMEOUT=5
GRUB_TERMINAL_OUTPUT="console"
GRUB_ENABLE_BLSCFG=true
EOF
cp "$root/etc/default/grub" "$root/original"
run fedora --yes zoro
check "theme path" "$(effective fedora GRUB_THEME)" "$root/boot/grub2/themes/one-piece/theme.txt"
check "graphical terminal" "$(effective fedora GRUB_TERMINAL_OUTPUT)" "gfxterm"
check "native resolution" "$(effective fedora GRUB_GFXMODE)" "2560x1440,auto"
check "timeout kept" "$(effective fedora GRUB_TIMEOUT)" "5"
check "os-prober enabled" "$(effective fedora GRUB_DISABLE_OS_PROBER)" "false"
check "os-prober installed for Windows" "$(grep -c 'dnf install -y os-prober' "$root/pkg.log")" "1"
check "menu_auto_hide cleared" "$(grep -c 'grub2-editenv - unset menu_auto_hide' "$root/pkg.log")" "1"
check "grub.cfg regenerated" "$(grep -c "grub2-mkconfig -o $root/boot/grub2/grub.cfg" "$root/mkconfig.log")" "1"
check "zoro background" "$(cmp -s "$root/boot/grub2/themes/one-piece/background.png" "$REPO/backgrounds/zoro.png" && echo same)" "same"
check "global command" "$(readlink "$root/usr/bin/onepiece-setup")" "$root/share/op/setup"
run fedora sea
check "switch theme" "$(cat "$root/share/op/installed")" "sea"
check "single config block" "$(grep -c 'one-piece-grub >>>' "$root/etc/default/grub")" "1"
run fedora remove
check "remove restores /etc/default/grub" "$(cmp -s "$root/etc/default/grub" "$root/original" && echo same)" "same"
check "remove deletes theme" "$(test -e "$root/boot/grub2/themes/one-piece" && echo exists || echo gone)" "gone"

# shellcheck disable=SC2016
GRUBD_LOOP='for x in ${sysconfdir}/default/grub.d/*.cfg'

echo "Kali (grub.d with its own theme)"
root="$(make_system kali grub-mkconfig 'ID=kali
ID_LIKE=debian
PRETTY_NAME="Kali GNU/Linux Rolling"' "$GRUBD_LOOP")"
mkdir -p "$root/etc/default/grub.d"
printf 'GRUB_TIMEOUT=5\n' > "$root/etc/default/grub"
printf 'GRUB_THEME=/boot/grub/themes/kali/theme.txt\n' > "$root/etc/default/grub.d/kali-themes.cfg"
cp "$root/etc/default/grub" "$root/original"
run kali wanted
check "overrides Kali theme" "$(effective kali GRUB_THEME)" "$root/boot/grub/themes/one-piece/theme.txt"
check "/etc/default/grub untouched" "$(cmp -s "$root/etc/default/grub" "$root/original" && echo same)" "same"
check "default resolution" "$(effective kali GRUB_GFXMODE)" "1920x1080,auto"
check "no Windows, no package install" "$(cat "$root/pkg.log" 2>/dev/null | grep -c apt-get || true)" "0"
run kali remove
check "remove deletes drop-in" "$(test -e "$root/etc/default/grub.d/zz-one-piece.cfg" && echo exists || echo gone)" "gone"

echo "Ubuntu (hidden menu, timeout 0)"
root="$(make_system ubuntu grub-mkconfig 'ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 24.04 LTS"' "$GRUBD_LOOP")"
mkdir -p "$root/etc/default/grub.d"
printf 'GRUB_TIMEOUT_STYLE=hidden\nGRUB_TIMEOUT=0\nGRUB_GFXMODE=1366x768\n' > "$root/etc/default/grub"
run ubuntu straw-hat
check "menu visible" "$(effective ubuntu GRUB_TIMEOUT_STYLE)" "menu"
check "timeout raised" "$(effective ubuntu GRUB_TIMEOUT)" "10"
check "user gfxmode kept" "$(effective ubuntu GRUB_GFXMODE)" "1366x768"

echo "Errors"
run ubuntu nope || true
check "unknown theme rejected" "$(grep -c 'Unknown theme: nope' "$TMP/ubuntu/out.log")" "1"
"$REPO/setup" build merry "$TMP/build" > /dev/null
check "build with alias" "$(head -1 "$TMP/build/theme.txt")" "# One Piece GRUB theme - goingmerry"

exit "$FAIL"
