#!/usr/bin/env python3
"""Build larger sizes of onepiece.pf2 (16px) so menus stay readable at 1080p.

Each glyph bitmap is upscaled with smoothing and re-thresholded, which keeps
the curves rounder than plain pixel doubling. Writes onepiece-<size>.pf2.

    python3 tools/scale_font.py 24 32
"""
import os
import struct
import sys

from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def sections(data):
    pos = 0
    while pos < len(data):
        name = data[pos:pos + 4].decode()
        ln = struct.unpack(">I", data[pos + 4:pos + 8])[0]
        if name == "DATA":
            return
        yield name, data[pos + 8:pos + 8 + ln]
        pos += 8 + ln


def read_font(path):
    data = open(path, "rb").read()
    info, glyphs = {}, []
    for name, body in sections(data):
        if name == "CHIX":
            for i in range(0, len(body), 9):
                code, flags, off = struct.unpack(">IBI", body[i:i + 9])
                w, h, xo, yo, dw = struct.unpack(">HHhhh", data[off:off + 10])
                bits = data[off + 10:off + 10 + (w * h + 7) // 8]
                glyphs.append((code, flags, w, h, xo, yo, dw, bits))
        else:
            info[name] = body
    return info, glyphs


def scale_glyph(w, h, xo, yo, dw, bits, f):
    nw, nh = max(1, round(w * f)), max(1, round(h * f))
    if w == 0 or h == 0:
        return 0, 0, round(xo * f), round(yo * f), round(dw * f), b""
    im = Image.new("L", (w, h), 0)
    px = im.load()
    for j in range(h):
        for i in range(w):
            n = j * w + i
            if bits[n >> 3] & (0x80 >> (n & 7)):
                px[i, j] = 255
    big = im.resize((nw * 4, nh * 4), Image.BICUBIC).resize((nw, nh), Image.BOX)
    out = bytearray((nw * nh + 7) // 8)
    bp = big.load()
    for j in range(nh):
        for i in range(nw):
            if bp[i, j] >= 128:
                n = j * nw + i
                out[n >> 3] |= 0x80 >> (n & 7)
    return nw, nh, round(xo * f), round(yo * f), round(dw * f), bytes(out)


def write_font(path, info, glyphs, size):
    def sec(name, body):
        return name.encode() + struct.pack(">I", len(body)) + body

    f = size / struct.unpack(">H", info["PTSZ"])[0]
    family = info["FAMI"].rstrip(b"\0").decode()
    head = b"".join([
        sec("FILE", b"PFF2"),
        sec("NAME", ("%s Regular %d" % (family, size)).encode() + b"\0"),
        sec("FAMI", info["FAMI"]),
        sec("WEIG", info["WEIG"]),
        sec("SLAN", info["SLAN"]),
        sec("PTSZ", struct.pack(">H", size)),
        sec("MAXW", struct.pack(">H", round(struct.unpack(">H", info["MAXW"])[0] * f))),
        sec("MAXH", struct.pack(">H", round(struct.unpack(">H", info["MAXH"])[0] * f))),
        sec("ASCE", struct.pack(">H", round(struct.unpack(">H", info["ASCE"])[0] * f))),
        sec("DESC", struct.pack(">H", round(struct.unpack(">H", info["DESC"])[0] * f))),
    ])
    scaled = [(g[0], g[1]) + scale_glyph(*g[2:], f) for g in glyphs]
    chix_len = 9 * len(scaled)
    offset = len(head) + 8 + chix_len + 8
    chix, blob = bytearray(), bytearray()
    for code, flags, w, h, xo, yo, dw, bits in scaled:
        chix += struct.pack(">IBI", code, flags, offset + len(blob))
        blob += struct.pack(">HHhhh", w, h, xo, yo, dw) + bits
    with open(path, "wb") as fh:
        fh.write(head + sec("CHIX", bytes(chix)) + b"DATA" + b"\xff\xff\xff\xff" + bytes(blob))


def main():
    info, glyphs = read_font(os.path.join(ROOT, "onepiece.pf2"))
    for size in map(int, sys.argv[1:] or ["24", "32"]):
        out = os.path.join(ROOT, "onepiece-%d.pf2" % size)
        write_font(out, info, glyphs, size)
        print(os.path.relpath(out, ROOT))


if __name__ == "__main__":
    main()
