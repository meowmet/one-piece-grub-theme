#!/usr/bin/env python3
"""Draw the One Piece styled distro icons (64x64) into icons/.

Every icon is a different object from the One Piece world, tinted with the
colours of the distribution it stands for. Drawn at 512px and downscaled.

    python3 tools/make_icons.py
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

N = 512
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "icons")
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
INK = "#1c120a"


def canvas():
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def save(im, name):
    # soft drop shadow so icons stay readable on bright backgrounds
    alpha = im.split()[3]
    shadow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    shadow.putalpha(alpha.point(lambda a: a * 0.55))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(shadow, (8, 10))
    out.alpha_composite(im)
    out.resize((64, 64), Image.LANCZOS).save(os.path.join(OUT, name + ".png"), optimize=True)


def pt(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def katana(d, x0, y0, x1, y1, blade, hilt, guard):
    """Sword from hilt end (x0,y0) to tip (x1,y1)."""
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    h = 0.27 * L
    gx, gy = x0 + ux * h, y0 + uy * h
    # blade with a slight curve
    w = 24
    pts = [(gx + nx * w, gy + ny * w)]
    for i in range(1, 11):
        t = i / 10
        bend = math.sin(t * math.pi) * 10
        px = gx + (x1 - gx) * t + nx * (w * (1 - t * 0.85) + bend)
        py = gy + (y1 - gy) * t + ny * (w * (1 - t * 0.85) + bend)
        pts.append((px, py))
    for i in range(10, -1, -1):
        t = i / 10
        bend = math.sin(t * math.pi) * 10
        px = gx + (x1 - gx) * t - nx * (w * (1 - t) - bend)
        py = gy + (y1 - gy) * t - ny * (w * (1 - t) - bend)
        pts.append((px, py))
    d.polygon(pts, fill=blade, outline=INK)
    d.line([(gx + ux * 10 + nx * 4, gy + uy * 10 + ny * 4), (x1 - ux * 30, y1 - uy * 30)], fill="#ffffff", width=4)
    # handle with diamond wrapping
    d.line([(x0, y0), (gx, gy)], fill=INK, width=44)
    d.line([(x0, y0), (gx, gy)], fill=hilt, width=34)
    for i in range(1, 6):
        t = i / 6
        cx, cy = x0 + (gx - x0) * t, y0 + (gy - y0) * t
        d.polygon([(cx + ux * 8, cy + uy * 8), (cx + nx * 10, cy + ny * 10),
                   (cx - ux * 8, cy - uy * 8), (cx - nx * 10, cy - ny * 10)], fill=INK)
    # tsuba (guard)
    d.ellipse((gx - 26, gy - 26, gx + 26, gy + 26), fill=guard, outline=INK, width=6)


def fedora():
    """Ship's helm with the Fedora 'f' in the hub."""
    im, d = canvas()
    c = N / 2
    wood, dark = "#a0612b", "#5b3412"
    for k in range(8):
        a = k * 45 + 22.5
        x0, y0 = pt(c, c, 120, a)
        x1, y1 = pt(c, c, 238, a)
        d.line([(x0, y0), (x1, y1)], fill=dark, width=40)
        d.line([(x0, y0), (x1, y1)], fill=wood, width=28)
        kx, ky = pt(c, c, 222, a)
        d.ellipse((kx - 26, ky - 26, kx + 26, ky + 26), fill=wood, outline=dark, width=7)
    d.ellipse((c - 188, c - 188, c + 188, c + 188), outline=dark, width=50)
    d.ellipse((c - 186, c - 186, c + 186, c + 186), outline=wood, width=36)
    d.ellipse((c - 176, c - 176, c + 176, c + 176), outline="#c9844a", width=6)
    for k in range(8):
        a = k * 45 + 22.5
        x0, y0 = pt(c, c, 60, a)
        x1, y1 = pt(c, c, 160, a)
        d.line([(x0, y0), (x1, y1)], fill=dark, width=30)
        d.line([(x0, y0), (x1, y1)], fill=wood, width=18)
    d.ellipse((c - 108, c - 108, c + 108, c + 108), fill="#294172", outline=INK, width=8)
    d.ellipse((c - 92, c - 92, c + 92, c + 92), fill="#51a2da")
    font = ImageFont.truetype(BOLD, 150)
    d.text((c + 4, c + 8), "f", font=font, fill="#ffffff", anchor="mm")
    return im


def endeavouros():
    """Gomu Gomu no Mi devil fruit in EndeavourOS purple."""
    im, d = canvas()
    cx, cy = 256, 290
    base, light, line = "#7f3fbf", "#b37be6", "#3d1466"
    # fruit made of a few bumps
    for ox, oy, r in ((-70, 30, 130), (70, 30, 130), (0, -40, 140), (0, 80, 130)):
        d.ellipse((cx + ox - r, cy + oy - r, cx + ox + r, cy + oy + r), fill=line)
    for ox, oy, r in ((-70, 30, 120), (70, 30, 120), (0, -40, 130), (0, 80, 120)):
        d.ellipse((cx + ox - r, cy + oy - r, cx + ox + r, cy + oy + r), fill=base)
    # devil fruit swirls
    def swirl(sx, sy, s, rot):
        pts = []
        for i in range(60):
            t = i / 59 * 2.2 * math.pi
            r = s * (0.15 + t / (2.2 * math.pi))
            pts.append(pt(sx, sy, r, math.degrees(t) + rot))
        d.line(pts, fill=light, width=12, joint="curve")
    swirl(cx - 70, cy + 40, 70, 0)
    swirl(cx + 75, cy + 35, 70, 120)
    swirl(cx, cy - 50, 70, 240)
    swirl(cx + 5, cy + 115, 55, 60)
    # curly stem and leaf
    d.line([(cx, cy - 165), (cx + 10, cy - 210), (cx + 40, cy - 230)], fill="#2f6b1f", width=22, joint="curve")
    d.ellipse((cx - 120, cy - 250, cx - 10, cy - 190), fill="#4caf50", outline="#1e4d14", width=7)
    d.line([(cx - 110, cy - 220), (cx - 20, cy - 220)], fill="#1e4d14", width=5)
    return im


def zorin():
    """Zoro's three swords crossed over Zorin blue."""
    im, d = canvas()
    katana(d, 40, 480, 470, 50, "#e9eef2", "#f4f4f4", "#d4af37")   # Wado Ichimonji
    katana(d, 472, 480, 42, 50, "#e9eef2", "#7a1414", "#3a3a3a")   # Sandai Kitetsu
    katana(d, 256, 506, 256, 8, "#e9eef2", "#111111", "#b08d2a")   # Shusui
    d.ellipse((126, 126, 386, 386), fill="#0b4f7d", outline=INK, width=10)
    d.ellipse((142, 142, 370, 370), fill="#15a6f0")
    font = ImageFont.truetype(BOLD, 170)
    d.text((256, 262), "Z", font=font, fill="#ffffff", anchor="mm")
    return im


def manjaro():
    """Nami's tangerine with Manjaro green leaves."""
    im, d = canvas()
    cx, cy, r = 256, 290, 190
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill="#b34700")
    d.ellipse((cx - r + 12, cy - r + 12, cx + r - 12, cy + r - 12), fill="#f28c1b")
    d.ellipse((cx - 120, cy - 140, cx - 20, cy - 60), fill="#ffb658")
    for i in range(40):
        a = i * 37 % 360
        rr = (i * 53) % 150
        x, y = pt(cx, cy, rr, a)
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill="#d9740f")
    # leaves in Manjaro's block style
    g, dg = "#35bf5c", "#1e7a37"
    d.rectangle((248, 60, 268, 115), fill="#5b3412")
    d.polygon([(262, 95), (360, 40), (450, 70), (370, 120)], fill=g, outline=dg)
    d.line([(262, 95), (440, 70)], fill=dg, width=6)
    d.polygon([(250, 95), (160, 30), (80, 60), (150, 115)], fill=g, outline=dg)
    d.line([(250, 95), (90, 60)], fill=dg, width=6)
    return im


def opensuse():
    """Log Pose bracelet with a green glass dome."""
    im, d = canvas()
    # strap
    d.rounded_rectangle((20, 300, 492, 420), radius=50, fill="#4a2c12", outline=INK, width=8)
    for x in range(60, 470, 60):
        d.ellipse((x - 8, 352, x + 8, 368), fill="#d4af37")
    # base plate
    d.ellipse((126, 330, 386, 430), fill="#8a5a2b", outline=INK, width=8)
    # glass dome
    d.ellipse((136, 120, 376, 360), fill=(150, 214, 80, 120), outline="#2d5f0a", width=10)
    d.ellipse((176, 150, 226, 220), fill=(255, 255, 255, 170))
    # needle
    d.polygon([(256, 150), (236, 220), (276, 220)], fill="#c0221a", outline=INK)
    d.polygon([(256, 290), (240, 220), (272, 220)], fill="#e8e8e8", outline=INK)
    d.ellipse((242, 206, 270, 234), fill="#d4af37", outline=INK, width=4)
    return im


def pop():
    """Chopper's pink top hat with the doctor's cross, Pop!_OS teal band."""
    im, d = canvas()
    pink, dpink = "#f06ea9", "#9c2f63"
    # brim
    d.ellipse((30, 330, 482, 450), fill=dpink)
    d.ellipse((40, 330, 472, 440), fill=pink)
    # crown
    d.rounded_rectangle((110, 70, 402, 395), radius=60, fill=dpink)
    d.rounded_rectangle((122, 80, 390, 390), radius=54, fill=pink)
    d.ellipse((122, 50, 390, 130), fill="#f78bbd", outline=dpink, width=8)
    # teal band
    d.rectangle((122, 300, 390, 345), fill="#48b9c7", outline="#1f6f78", width=5)
    # white X
    d.line([(180, 140), (332, 280)], fill="#ffffff", width=52)
    d.line([(332, 140), (180, 280)], fill="#ffffff", width=52)
    d.line([(180, 140), (332, 280)], fill="#4a90d9", width=18)
    d.line([(332, 140), (180, 280)], fill="#4a90d9", width=18)
    return im


def elementary():
    """Den Den Mushi, the transponder snail."""
    im, d = canvas()
    body, dbody = "#f2d9a0", "#8a6a2c"
    # body
    d.rounded_rectangle((40, 330, 470, 440), radius=55, fill=dbody)
    d.rounded_rectangle((50, 336, 460, 430), radius=48, fill=body)
    # head and eye stalks
    d.line([(420, 340), (440, 200)], fill=dbody, width=26)
    d.line([(470, 340), (480, 210)], fill=dbody, width=26)
    d.line([(420, 340), (440, 200)], fill=body, width=16)
    d.line([(470, 340), (480, 210)], fill=body, width=16)
    for ex, ey in ((440, 195), (480, 205)):
        d.ellipse((ex - 22, ey - 22, ex + 22, ey + 22), fill="#ffffff", outline=INK, width=5)
        d.ellipse((ex - 8, ey - 8, ex + 8, ey + 8), fill=INK)
    # shell (elementary dark grey) with receiver
    d.ellipse((90, 90, 380, 380), fill="#1f1f1f")
    d.ellipse((102, 102, 368, 368), fill="#4d4d4d")
    for r in (110, 75, 40):
        d.arc((235 - r, 235 - r, 235 + r, 235 + r), 0, 300, fill="#d9d9d9", width=10)
    d.rounded_rectangle((150, 50, 330, 100), radius=25, fill="#f2f2f2", outline=INK, width=6)
    d.line([(240, 100), (240, 130)], fill=INK, width=8)
    return im


def centos():
    """Ship's anchor, CentOS purple."""
    im, d = canvas()
    metal, dark = "#932279", "#4a0f3c"
    c = 256
    d.ellipse((c - 50, 30, c + 50, 130), outline=dark, width=30)
    d.ellipse((c - 50, 30, c + 50, 130), outline=metal, width=18)
    d.rectangle((c - 22, 120, c + 22, 440), fill=dark)
    d.rectangle((c - 14, 120, c + 14, 436), fill=metal)
    d.rounded_rectangle((c - 130, 170, c + 130, 210), radius=18, fill=dark)
    d.rounded_rectangle((c - 122, 176, c + 122, 204), radius=14, fill=metal)
    d.arc((c - 200, 160, c + 200, 470), 20, 160, fill=dark, width=40)
    d.arc((c - 200, 160, c + 200, 470), 20, 160, fill=metal, width=26)
    for sx in (-1, 1):
        x = c + sx * 190
        d.polygon([(x + sx * 10, 270), (x - sx * 40, 360), (x + sx * 60, 350)], fill=metal, outline=dark, width=6)
    return im


def rocky():
    """Treasure chest, Rocky green trims."""
    im, d = canvas()
    wood, dwood, trim = "#8b5a2b", "#4a2c12", "#10b981"
    # gold heap
    for i, (x, y) in enumerate([(150, 170), (210, 140), (270, 130), (330, 150), (380, 180), (240, 175), (310, 185)]):
        d.ellipse((x - 40, y - 26, x + 40, y + 26), fill="#d4a017", outline="#7a5a00", width=5)
        d.ellipse((x - 18, y - 10, x + 10, y), fill="#fff0a0")
    d.ellipse((215, 70, 275, 130), fill="#e94e77", outline="#7a1a35", width=6)
    # lid
    d.chord((60, 120, 452, 330), 180, 360, fill=dwood)
    d.chord((72, 132, 440, 320), 180, 360, fill=wood)
    d.rectangle((60, 225, 452, 245), fill=trim)
    # box
    d.rectangle((60, 235, 452, 450), fill=dwood)
    d.rectangle((72, 245, 440, 438), fill=wood)
    for y in (300, 370):
        d.line([(72, y), (440, y)], fill=dwood, width=6)
    for x in (60, 432):
        d.rectangle((x, 230, x + 20, 450), fill=trim, outline=INK)
    d.rectangle((226, 240, 286, 320), fill="#d4af37", outline=INK, width=6)
    d.ellipse((246, 262, 266, 282), fill=INK)
    d.rectangle((252, 278, 260, 300), fill=INK)
    return im


def kernel():
    """Jolly Roger flag for plain kernel entries (Fedora BLS)."""
    im, d = canvas()
    d.rectangle((60, 30, 82, 490), fill="#6b4a2b", outline=INK, width=5)
    d.ellipse((50, 18, 92, 58), fill="#d4af37", outline=INK, width=5)
    pts = [(82, 70)]
    for i in range(0, 21):
        x = 82 + i * 19
        pts.append((x, 70 + math.sin(i / 3) * 14))
    for i in range(20, -1, -1):
        x = 82 + i * 19
        pts.append((x, 360 + math.sin(i / 3) * 14))
    d.polygon(pts, fill="#111111", outline="#000000")
    # skull and crossbones
    d.line([(160, 300), (380, 150)], fill="#f2f2f2", width=26)
    d.line([(160, 150), (380, 300)], fill="#f2f2f2", width=26)
    for x, y in ((160, 300), (380, 150), (160, 150), (380, 300)):
        d.ellipse((x - 20, y - 20, x + 20, y + 20), fill="#f2f2f2")
    d.ellipse((205, 110, 335, 230), fill="#f2f2f2")
    d.rounded_rectangle((230, 200, 310, 255), radius=12, fill="#f2f2f2")
    d.ellipse((232, 150, 262, 182), fill="#111111")
    d.ellipse((278, 150, 308, 182), fill="#111111")
    return im


def os_icon():
    """Compass rose, the generic fallback."""
    im, d = canvas()
    c = 256
    d.ellipse((30, 30, 482, 482), fill="#5b3412")
    d.ellipse((44, 44, 468, 468), fill="#f1e2bd")
    d.ellipse((70, 70, 442, 442), outline="#8a6a2c", width=6)
    for k in range(32):
        a = k * 11.25
        r0 = 190 if k % 2 else 175
        d.line([pt(c, c, r0, a), pt(c, c, 205, a)], fill="#8a6a2c", width=4)
    for k in range(4):
        a = k * 90 + 45
        d.polygon([pt(c, c, 130, a), pt(c, c, 26, a + 45), pt(c, c, 26, a - 45)], fill="#8a6a2c", outline=INK)
    for k, col in ((0, "#c0221a"), (1, "#2b2b2b"), (2, "#2b2b2b"), (3, "#2b2b2b")):
        a = k * 90 - 90
        d.polygon([pt(c, c, 185, a), pt(c, c, 34, a + 45), pt(c, c, 34, a - 45)], fill=col, outline=INK)
    d.ellipse((c - 20, c - 20, c + 20, c + 20), fill="#d4af37", outline=INK, width=5)
    return im


ICONS = {
    "fedora": fedora,
    "endeavouros": endeavouros,
    "zorin": zorin,
    "manjaro": manjaro,
    "opensuse": opensuse,
    "pop": pop,
    "elementary": elementary,
    "centos": centos,
    "rocky": rocky,
    "kernel": kernel,
    "os": os_icon,
}

if __name__ == "__main__":
    for name, draw in ICONS.items():
        save(draw(), name)
        print("icons/%s.png" % name)
