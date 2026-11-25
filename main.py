#!/usr/bin/env python3
"""news-image-20261124 poster edition for @lanzking.

Stdlib-only renderer: loads pre-baked glyph bitmaps from glyphs.bin,
draws a 1024x1024 breaking-news poster, writes entry.png.
"""
import os
import struct
import sys
import zlib

W = H = 1024
NAVY = (8, 18, 38)
PANEL = (17, 34, 66)
PANEL2 = (22, 44, 82)
RED = (206, 32, 48)
WHITE = (245, 248, 252)
LIGHT = (198, 214, 233)
GOLD = (242, 192, 84)
CYAN = (86, 190, 220)
GREEN = (70, 200, 130)
GREY = (140, 158, 182)

# ---- baked news data (Tuesday 24 November 2026) ----
HERO_HEAD = ["HORMUZ TANKERS", "HIT MINES"]
HERO_SUMMARY = ("Iran's Revolutionary Guard says three tankers struck "
                "mines late Monday despite a US escort - unconfirmed by US "
                "Central Command. The US sanctioned 24+ Iranian exchange "
                "houses; Tehran rules out talks until its seven conditions "
                "are met.")
TILES = [
    ("chip", "NVIDIA BRINGS BACK HUANG",
     "Jensen Huang reinstated as CEO days after saying he would retire; shares jump about 31%."),
    ("rocket", "SHENZHOU-24 AT TIANGONG",
     "Two Chinese astronauts and Pakistan's Zeeshan Ali - the station's first foreign visitor."),
    ("tower", "RIYADH TOWER HIT AGAIN",
     "Houthi strike on the tallest tower, second in a week, injures 11; coalition cries terrorism."),
    ("shield", "EU: 22ND RUSSIA PACKAGE",
     "Brussels proposes sanctions on about 60 more banks and crypto networks; needs all 27."),
    ("flag", "N. KOREA EXPELS SWISS ENVOY",
     "Pyongyang demands closure of Switzerland's new office and orders its top diplomat out."),
    ("peak", "5.6 QUAKE STRIKES NEPAL",
     "Earthquake hits Koshi province, near the border with China."),
]
WIDE_HEAD = "14 NATIONS BACK ICJ RULING ON ROHINGYA GENOCIDE"
WIDE_LINE = ("The court's Myanmar genocide finding is affirmed; Malaysia says it will "
             "return more than 6,500 Rohingya refugees to Myanmar.")
MARKETS = [
    ("S&P 500", "7,237.17", "+4.73%"),
    ("NASDAQ", "24,089.56", "+6.51%"),
    ("DAX", "25,337.27", "+2.15%"),
    ("FTSE 100", "10,480.82", "+1.30%"),
    ("BRENT", "$86.7", "-2.99%"),
    ("GOLD", "$3,620.4", "-0.85%"),
]

# ---- glyph loading ----
GLYPHS = {}


def load_glyphs():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "glyphs.bin")
    with open(path, "rb") as fh:
        data = fh.read()
    assert data[:4] == b"GLY1"
    (count,) = struct.unpack_from("<I", data, 4)
    off = 8
    for _ in range(count):
        font_id, size, cp, w, h = struct.unpack_from("<BHIHH", data, off)
        off += 11
        GLYPHS[(font_id, size, cp)] = (w, h, data[off:off + w * h])
        off += w * h


def text_w(text, font, size):
    total = 0
    for ch in text:
        g = GLYPHS.get((font, size, ord(ch)))
        if g is None:
            g = GLYPHS.get((font, size, 32))
        total += g[0]
    return total


# ---- pixel buffer ----
BUF = bytearray(W * H * 3)


def fill_rect(x, y, w, h, col):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(col) * (x1 - x0)
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        BUF[i:i + len(row)] = row


def ellipse(cx, cy, rx, ry, col):
    for yy in range(cy - ry, cy + ry + 1):
        if 0 <= yy < H:
            t = (yy - cy) / ry if ry else 0
            span = int(rx * (1 - t * t) ** 0.5)
            fill_rect(cx - span, yy, span * 2 + 1, 1, col)


def polygon(points, col):
    ys = [p[1] for p in points]
    for yy in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            if (y1 <= yy < y2) or (y2 <= yy < y1):
                xs.append(int(x1 + (yy - y1) * (x2 - x1) / (y2 - y1)))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            fill_rect(xs[i], yy, xs[i + 1] - xs[i] + 1, 1, col)


def thick_line(x1, y1, x2, y2, thick, col):
    steps = max(abs(x2 - x1), abs(y2 - y1), 1)
    r = max(1, thick // 2)
    for s in range(steps + 1):
        x = x1 + (x2 - x1) * s // steps
        y = y1 + (y2 - y1) * s // steps
        ellipse(x, y, r, r, col)


def draw_text(x, y, text, font, size, col):
    cx = x
    for ch in text:
        g = GLYPHS.get((font, size, ord(ch)))
        if g is None:
            g = GLYPHS.get((font, size, 32))
            if g is None:
                continue
        w, h, alpha = g
        for yy in range(h):
            py = y + yy
            if not (0 <= py < H):
                continue
            base = (py * W) * 3
            arow = yy * w
            for xx in range(w):
                a = alpha[arow + xx]
                if a:
                    px = cx + xx
                    if 0 <= px < W:
                        i = base + px * 3
                        if a == 255:
                            BUF[i] = col[0]; BUF[i + 1] = col[1]; BUF[i + 2] = col[2]
                        else:
                            ia = 255 - a
                            BUF[i] = (col[0] * a + BUF[i] * ia) // 255
                            BUF[i + 1] = (col[1] * a + BUF[i + 1] * ia) // 255
                            BUF[i + 2] = (col[2] * a + BUF[i + 2] * ia) // 255
        cx += w
    return cx


def centered(y, text, font, size, col):
    draw_text((W - text_w(text, font, size)) // 2, y, text, font, size, col)


def wrap(text, font, size, maxw):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if text_w(trial, font, size) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def line_h(size):
    g = GLYPHS.get((0, size, 65))
    return g[1] if g else size


# ---- illustration: tanker on a stylised strait ----
def draw_hero_art(x, y, w, h):
    fill_rect(x, y, w, h, (13, 44, 78))
    # strait banks
    polygon([(x, y), (x + 90, y), (x + 40, y + h), (x, y + h)], (30, 70, 60))
    polygon([(x + w, y), (x + w - 80, y), (x + w - 30, y + h), (x + w, y + h)], (30, 70, 60))
    # sea lanes
    for i in range(3):
        fill_rect(x + 70 + i * 8, y + 26 + i * 34, w - 140, 3, (40, 110, 150))
    # tanker hull + deck + containers
    polygon([(x + 78, y + 96), (x + w - 78, y + 96), (x + w - 104, y + 124),
             (x + 104, y + 124)], (24, 28, 38))
    fill_rect(x + 96, y + 82, w - 192, 14, RED)
    for i, c in enumerate([(220, 140, 50), (70, 160, 200), (90, 190, 120), (200, 90, 90)]):
        fill_rect(x + 108 + i * 52, y + 58, 44, 24, c)
    fill_rect(x + w - 128, y + 40, 26, 42, WHITE)
    fill_rect(x + w - 122, y + 46, 6, 6, NAVY)
    # mines: spiked circles
    for (mx, my) in [(x + 70, y + 148), (x + w - 66, y + 140), (x + w // 2, y + 156)]:
        ellipse(mx, my, 11, 11, (18, 20, 26))
        for dx, dy in [(0, -16), (11, -11), (16, 0), (11, 11), (0, 16), (-11, 11), (-16, 0), (-11, -11)]:
            thick_line(mx, my, mx + dx, my + dy, 3, (18, 20, 26))
        ellipse(mx - 3, my - 3, 3, 3, RED)
    # waves
    for i in range(4):
        fill_rect(x + 44 + i * 74, y + h - 18, 44, 4, CYAN)


def draw_icon(kind, x, y):
    if kind == "chip":
        fill_rect(x, y, 34, 34, CYAN)
        fill_rect(x + 8, y + 8, 18, 18, NAVY)
        for i in range(3):
            fill_rect(x - 6, y + 5 + i * 11, 6, 3, CYAN)
            fill_rect(x + 34, y + 5 + i * 11, 6, 3, CYAN)
    elif kind == "rocket":
        polygon([(x + 17, y - 4), (x + 30, y + 26), (x + 4, y + 26)], WHITE)
        ellipse(x + 17, y + 34, 8, 12, (240, 140, 60))
        ellipse(x + 17, y + 12, 5, 5, CYAN)
    elif kind == "tower":
        fill_rect(x + 10, y - 6, 14, 46, GOLD)
        polygon([(x + 17, y - 18), (x + 24, y - 6), (x + 10, y - 6)], RED)
        for i in range(4):
            fill_rect(x + 14, y + 2 + i * 9, 6, 4, NAVY)
    elif kind == "shield":
        ellipse(x + 17, y + 17, 18, 18, (90, 140, 220))
        draw_text(x + 10, y + 6, "E", 0, 24, WHITE)
    elif kind == "flag":
        fill_rect(x + 4, y - 8, 4, 48, WHITE)
        polygon([(x + 8, y - 8), (x + 36, y + 0), (x + 8, y + 10)], RED)
        fill_rect(x + 16, y - 4, 8, 8, WHITE)
    elif kind == "peak":
        polygon([(x + 17, y - 10), (x + 38, y + 38), (x - 4, y + 38)], (170, 185, 205))
        polygon([(x + 17, y - 10), (x + 24, y + 4), (x + 10, y + 4)], WHITE)
    else:
        ellipse(x + 17, y + 17, 16, 16, GOLD)


def build():
    fill_rect(0, 0, W, H, NAVY)
    # top breaking band
    fill_rect(0, 0, W, 58, RED)
    centered(10, "BREAKING NEWS", 0, 34, WHITE)
    fill_rect(0, 58, W, 5, GOLD)
    # date block
    centered(74, "24 NOVEMBER 2026", 0, 64, WHITE)
    centered(148, "TUESDAY  -  THE WORLD IN ONE IMAGE", 0, 21, GOLD)
    # hero panel
    hx, hy, hw, hh = 30, 188, 964, 258
    fill_rect(hx, hy, hw, hh, PANEL)
    fill_rect(hx, hy, 9, hh, RED)
    draw_text(hx + 28, hy + 16, "LEAD STORY - IRAN / STRAIT OF HORMUZ", 0, 19, GOLD)
    yy = hy + 42
    for line in HERO_HEAD:
        draw_text(hx + 28, yy, line, 0, 52, WHITE)
        yy += line_h(52) - 6
    sy = yy + 2
    for line in wrap(HERO_SUMMARY, 1, 17, 566):
        draw_text(hx + 28, sy, line, 1, 17, LIGHT)
        sy += line_h(17) + 2
    draw_hero_art(hx + 610, hy + 44, 326, 196)
    # story grid: 2 columns x 3 rows
    gx, gy, tw, th, gap = 30, 458, 478, 98, 8
    for idx, (icon, head, line) in enumerate(TILES):
        tx = gx + (idx % 2) * (tw + gap)
        ty = gy + (idx // 2) * (th + gap)
        fill_rect(tx, ty, tw, th, PANEL2 if idx % 2 == 0 else PANEL)
        fill_rect(tx, ty, tw, 4, CYAN if idx % 2 == 0 else GOLD)
        draw_icon(icon, tx + 30, ty + 34)
        lines = wrap(head, 0, 21, 386)
        ly = ty + 10
        for ln in lines[:2]:
            draw_text(tx + 82, ly, ln, 0, 21, WHITE)
            ly += line_h(21) + 1
        for ln in wrap(line, 1, 17, 386)[:2]:
            draw_text(tx + 82, ly, ln, 1, 17, LIGHT)
            ly += line_h(17) + 1
    # wide tile: Myanmar / ICJ (two-line body so nothing overflows)
    wy = gy + 3 * (th + gap) + 4
    fill_rect(30, wy, 964, 78, PANEL)
    fill_rect(30, wy, 9, 78, GOLD)
    draw_text(58, wy + 7, WIDE_HEAD, 0, 21, WHITE)
    draw_text(58, wy + 34, "The court's Myanmar genocide finding is affirmed; "
              "Malaysia says it will return", 1, 17, LIGHT)
    draw_text(58, wy + 55, "more than 6,500 Rohingya refugees to Myanmar.",
              1, 17, LIGHT)
    # markets ticker strip: closing figures, Tuesday 24 Nov 2026
    ty0 = wy + 88
    fill_rect(0, ty0, W, 102, (20, 40, 74))
    fill_rect(0, ty0, W, 4, GOLD)
    draw_text(30, ty0 + 10, "MARKETS AT THE CLOSE", 0, 19, GOLD)
    for idx, (name, value, change) in enumerate(MARKETS):
        mx = 30 + (idx % 3) * 338
        my = ty0 + 38 + (idx // 3) * 30
        cx = draw_text(mx, my, name, 0, 19, WHITE)
        cx = draw_text(cx + 10, my, value, 1, 19, LIGHT)
        ch_col = GREEN if change.startswith("+") else (240, 110, 110)
        draw_text(cx + 10, my, change, 0, 19, ch_col)
    # footer
    centered(ty0 + 110, "All stories verified against the day's reporting.",
             1, 17, GREY)


def write_png(path):
    raw = bytearray()
    row_bytes = W * 3
    for yy in range(H):
        raw.append(0)
        raw += BUF[yy * row_bytes:(yy + 1) * row_bytes]

    def chunk(tag, payload):
        c = struct.pack(">I", len(payload)) + tag + payload
        c += struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)
        return c

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)


def main():
    load_glyphs()
    build()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "entry.png")
        write_png(path)
    except OSError:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "entry.png")
        write_png(path)
    print("wrote", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
