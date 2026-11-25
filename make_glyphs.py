#!/usr/bin/env python3
"""Build-time glyph generator (uses Pillow; NOT imported by main.py).

Produces glyphs.bin with a simple documented format:

  Header:  magic b'GLY1' (4 bytes), u32 little-endian glyph count
  Per glyph record:
    u8   font_id   (0=Sans Bold, 1=Sans Regular, 2=Serif Bold)
    u16  size      (pixels)
    u32  codepoint (Unicode code point)
    u16  width     (bitmap width == advance width, px)
    u16  height    (bitmap height == ascent+descent line height, px)
    bytes width*height  8-bit alpha values, row-major

Each glyph is rendered into a box of (advance x line_height) so the
runtime in main.py can blit boxes left-to-right with no metrics maths.
Characters: ASCII 32-126 plus curly quotes, en/em dashes, bullet,
ellipsis, pound and euro signs.
"""
import struct
from PIL import Image, ImageDraw, ImageFont

FONTS = {
    0: "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    1: "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    2: "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
}
SIZES = [17, 19, 21, 24, 28, 34, 42, 52, 64]
EXTRA = [0x2018, 0x2019, 0x201C, 0x201D, 0x2013, 0x2014, 0x2022,
         0x2026, 0x00A3, 0x20AC, 0x00B7, 0x2191, 0x2193]
CODEPOINTS = list(range(32, 127)) + EXTRA


def main():
    records = []
    for font_id, path in FONTS.items():
        for size in SIZES:
            font = ImageFont.truetype(path, size)
            ascent, descent = font.getmetrics()
            line_h = ascent + descent
            for cp in CODEPOINTS:
                ch = chr(cp)
                adv = max(1, int(round(font.getlength(ch))))
                img = Image.new("L", (adv, line_h), 0)
                draw = ImageDraw.Draw(img)
                draw.text((0, 0), ch, fill=255, font=font)
                records.append((font_id, size, cp, adv, line_h,
                                img.tobytes()))
    with open("glyphs.bin", "wb") as fh:
        fh.write(b"GLY1")
        fh.write(struct.pack("<I", len(records)))
        for font_id, size, cp, w, h, data in records:
            fh.write(struct.pack("<BHIHH", font_id, size, cp, w, h))
            fh.write(data)
    print("glyphs:", len(records))


if __name__ == "__main__":
    main()
