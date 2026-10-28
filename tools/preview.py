#!/usr/bin/env python3
"""Render an approximate 1920x1080 preview of every theme into previews/.

Uses the real bitmap font (onepiece.pf2), pixmaps and icons, so what you see is
close to what GRUB draws.

    python3 tools/preview.py
"""
import os
import re
import struct

from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
W, H = 1920, 1080
ENTRIES = [
    ("Fedora Linux (6.11.4-301.fc41.x86_64)", "fedora"),
    ("Ubuntu", "ubuntu"),
    ("Windows Boot Manager (on /dev/nvme0n1p1)", "windows"),
    ("Advanced options for Ubuntu", None),
    ("UEFI Firmware Settings", "efi"),
]


class PF2:
    def __init__(self, path):
        data = open(path, "rb").read()
        pos, self.chars, self.ascent = 0, {}, 0
        while pos < len(data):
            name, ln = data[pos:pos + 4].decode(), struct.unpack(">I", data[pos + 4:pos + 8])[0]
            body = data[pos + 8:pos + 8 + ln] if name != "DATA" else None
            if name == "NAME":
                self.name = body.rstrip(b"\0").decode()
            elif name == "ASCE":
                self.ascent = struct.unpack(">H", body)[0]
            elif name == "CHIX":
                for i in range(0, ln, 9):
                    code, _, off = struct.unpack(">IBI", body[i:i + 9])
                    self.chars[code] = off
            if name == "DATA":
                break
            pos += 8 + ln
        self.data = data

    def glyph(self, ch):
        off = self.chars.get(ord(ch)) or self.chars.get(ord("?"))
        w, h, xo, yo, dw = struct.unpack(">HHhhh", self.data[off:off + 10])
        bits = self.data[off + 10:off + 10 + (w * h + 7) // 8]
        return w, h, xo, yo, dw, bits

    def width(self, text):
        return sum(self.glyph(c)[4] for c in text)

    def draw(self, im, x, y_top, text, color):
        base = y_top + self.ascent
        px = im.load()
        for ch in text:
            w, h, xo, yo, dw, bits = self.glyph(ch)
            for j in range(h):
                for i in range(w):
                    n = j * w + i
                    if bits[n >> 3] & (0x80 >> (n & 7)):
                        X, Y = x + xo + i, base - yo - h + j
                        if 0 <= X < W and 0 <= Y < H:
                            px[X, Y] = color
            x += dw


def hexc(s):
    s = s.strip('"').lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def dim(v, total):
    v = v.strip('"').replace(" ", "")
    m = re.match(r"(\d+)%([+-]\d+)?$", v)
    if m:
        return int(total * int(m.group(1)) / 100) + int(m.group(2) or 0)
    return int(v)


def parse(path):
    blocks, cur = [], None
    for line in open(path):
        line = line.strip()
        if line.startswith("+"):
            cur = {"type": line[1:].strip(" {")}
            blocks.append(cur)
        elif line == "}":
            cur = None
        elif cur is not None and "=" in line:
            k, v = line.split("=", 1)
            cur[k.strip()] = v.strip().strip('"')
    return blocks


def pixmap_box(im, d, style, x, y, w, h):
    def piece(k):
        p = os.path.join(d, style.replace("*", k))
        return Image.open(p).convert("RGBA") if os.path.exists(p) else None
    nw, ne, sw, se = piece("nw"), piece("ne"), piece("sw"), piece("se")
    wl = piece("w").width if piece("w") else 0
    er = piece("e").width if piece("e") else 0
    tn = piece("n").height if piece("n") else 0
    bs = piece("s").height if piece("s") else 0
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    def put(p, bx, by, bw, bh):
        if p and bw > 0 and bh > 0:
            layer.paste(p.resize((bw, bh)), (bx, by))
    put(nw, x, y, wl, tn); put(piece("n"), x + wl, y, w - wl - er, tn); put(ne, x + w - er, y, er, tn)
    put(piece("w"), x, y + tn, wl, h - tn - bs); put(piece("c"), x + wl, y + tn, w - wl - er, h - tn - bs)
    put(piece("e"), x + w - er, y + tn, er, h - tn - bs)
    put(sw, x, y + h - bs, wl, bs); put(piece("s"), x + wl, y + h - bs, w - wl - er, bs); put(se, x + w - er, y + h - bs, er, bs)
    im.alpha_composite(layer)


def render(theme_dir, background, fonts, out):
    im = Image.open(background).convert("RGBA").resize((W, H))
    for b in parse(os.path.join(theme_dir, "theme.txt")):
        x, y = dim(b.get("left", "0"), W), dim(b.get("top", "0"), H)
        w = dim(b.get("width", "100%"), W)
        font = fonts.get(b.get("font", b.get("item_font", "")), fonts["ONE PIECE Regular 16"])
        if b["type"] == "label":
            text = b["text"].replace("%d", "10")
            tw = font.width(text)
            tx = x + w - tw if b.get("align") == "right" else x + (w - tw) // 2 if b.get("align") == "center" else x
            font.draw(im, tx, y, text, hexc(b["color"]))
        elif b["type"] == "boot_menu":
            h = dim(b["height"], H)
            if "menu_pixmap_style" in b:
                pixmap_box(im, theme_dir, b["menu_pixmap_style"], x, y, w, h)
            ih, sp, pad = int(b["item_height"]), int(b["item_spacing"]), int(b["item_padding"])
            iw, gap = int(b["icon_width"]), int(b["item_icon_space"])
            cy = y + 14
            for i, (label, icon) in enumerate(ENTRIES):
                if i == 0:
                    pixmap_box(im, theme_dir, b["selected_item_pixmap_style"], x + 10, cy, w - 20, ih)
                if icon:
                    path = os.path.join(theme_dir, "icons", icon + ".png")
                    if not os.path.exists(path):
                        path = os.path.join(ROOT, "icons", icon + ".png")
                    ic = Image.open(path).convert("RGBA").resize((iw, iw))
                    im.alpha_composite(ic, (x + 10 + pad, cy + (ih - iw) // 2))
                color = hexc(b["selected_item_color"] if i == 0 else b["item_color"])
                font.draw(im, x + 10 + pad + iw + gap, cy + (ih - font.ascent) // 2, label, color)
                cy += ih + sp
    im.convert("RGB").save(out, quality=85)


def main():
    fonts = {}
    for f in os.listdir(ROOT):
        if f.endswith(".pf2"):
            pf = PF2(os.path.join(ROOT, f))
            fonts[pf.name] = pf
    os.makedirs(os.path.join(ROOT, "previews"), exist_ok=True)
    for name in sorted(os.listdir(os.path.join(ROOT, "themes"))):
        tdir = os.path.join(ROOT, "themes", name)
        bg = open(os.path.join(tdir, "background")).read().strip()
        # luffy is the original theme and uses the files in the repository root
        if not os.path.exists(os.path.join(tdir, "select_c.png")):
            tdir = ROOT
        render(tdir, os.path.join(ROOT, "backgrounds", bg + ".png"), fonts,
               os.path.join(ROOT, "previews", name + ".jpg"))
        print("previews/%s.jpg" % name)


if __name__ == "__main__":
    main()
