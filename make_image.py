#!/usr/bin/env python3
"""Render the front page of THE WORLD TODAY for 17 November 2026.

Draws a 1024x1024 newspaper front page with Pillow and saves it as
entry.png in this directory. Every drawing call is deterministic: no
randomness, no timestamps, no network.
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (20, 20, 20)
RED = (178, 34, 34)
NAVY = (31, 42, 68)
GREY = (90, 86, 76)
PANEL = (255, 253, 246)
SEA = (46, 98, 140)
GOLD = (201, 162, 39)

FONT_DIR = "/usr/share/fonts/truetype/noto"
SERIF_BLACK = os.path.join(FONT_DIR, "NotoSerif-Black.ttf")
SERIF_BOLD = os.path.join(FONT_DIR, "NotoSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "NotoSerif-Regular.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "NotoSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, path, max_size, max_width, max_lines):
    """Largest font size (down from max_size) whose wrap fits max_lines."""
    for size in range(max_size, 15, -1):
        fnt = font(path, size)
        lines = wrap(draw, text, fnt, max_width)
        if len(lines) <= max_lines:
            return fnt, lines
    fnt = font(path, 16)
    return fnt, wrap(draw, text, fnt, max_width)


def centre(draw, y, text, fnt, fill, cx=W // 2):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return y + fnt.size


def draw_flag(draw, x, y, w, h, kind):
    """A small flag on a pole at (x, y), w x h, kind in CN/US/RU."""
    draw.line([(x + w // 2, y), (x + w // 2, y - 34)], fill=INK, width=3)
    if kind == "CN":
        draw.rectangle([x, y - 34, x + w, y - 34 + h], fill=(222, 41, 16))
        draw.text((x + 4, y - 34 + 2), "\u2605", font=font(SANS_BOLD, 12),
                  fill=(255, 222, 0))
    elif kind == "US":
        for i in range(7):
            col = (178, 34, 52) if i % 2 == 0 else (255, 255, 255)
            draw.rectangle([x, y - 34 + i * h // 7, x + w,
                            y - 34 + (i + 1) * h // 7], fill=col)
        draw.rectangle([x, y - 34, x + w // 2, y - 34 + 4 * h // 7],
                       fill=(60, 59, 110))
    else:  # RU
        for i, col in enumerate([(255, 255, 255), (0, 57, 166),
                                (213, 0, 50)]):
            draw.rectangle([x, y - 34 + i * h // 3, x + w,
                            y - 34 + (i + 1) * h // 3], fill=col)
    draw.rectangle([x, y - 34, x + w, y - 34 + h], outline=INK, width=1)


def draw_bridge(draw, x, y, w, h):
    """Kerch bridge with a broken span: deck, towers, sea, smoke."""
    draw.rectangle([x, y + h - 46, x + w, y + h], fill=SEA)
    for i in range(3):
        sx = x + 20 + i * 52
        draw.arc([sx, y + h - 66, sx + 44, y + h - 22], 180, 360,
                 fill=(255, 255, 255), width=3)
    # towers
    for tx in (x + 62, x + w - 82):
        draw.rectangle([tx, y + 22, tx + 16, y + h - 46], fill=(70, 70, 70))
    # deck in two pieces with a gap in the middle
    draw.rectangle([x, y + 78, x + w // 2 - 26, y + 92], fill=(40, 40, 40))
    draw.rectangle([x + w // 2 + 26, y + 78, x + w, y + 92], fill=(40, 40, 40))
    # cables
    for cx in range(x + 10, x + w // 2 - 30, 26):
        draw.line([(cx, y + 78), (x + 70, y + 26)], fill=GREY, width=2)
    for cx in range(x + w // 2 + 34, x + w - 6, 26):
        draw.line([(cx, y + 78), (x + w - 74, y + 26)], fill=GREY, width=2)
    # smoke from the gap
    for i, r in enumerate((16, 12, 9)):
        cx = x + w // 2 + (i - 1) * 8
        cy = y + 58 - i * 12
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 120, 120))
    # red burst marker
    draw.ellipse([x + w // 2 - 10, y + 66, x + w // 2 + 10, y + 86],
                 fill=RED)


def draw_tanker(draw, x, y, w, h):
    """Oil tanker on a blue sea, flames and smoke above the deck."""
    draw.rectangle([x, y + h - 40, x + w, y + h], fill=SEA)
    for i in range(3):
        sx = x + 16 + i * 58
        draw.arc([sx, y + h - 58, sx + 46, y + h - 18], 180, 360,
                 fill=(255, 255, 255), width=3)
    # hull
    draw.polygon([(x + 12, y + 96), (x + w - 12, y + 96),
                  (x + w - 34, y + 128), (x + 34, y + 128)], fill=(32, 32, 40))
    draw.rectangle([x + 12, y + 88, x + w - 12, y + 96], fill=(178, 34, 34))
    # containers
    for i, col in enumerate([(201, 162, 39), (46, 98, 140), (201, 162, 39)]):
        draw.rectangle([x + 52 + i * 62, y + 58, x + 104 + i * 62, y + 88],
                       fill=col, outline=INK, width=1)
    # funnel with smoke
    draw.rectangle([x + w - 62, y + 52, x + w - 38, y + 88], fill=(60, 60, 60))
    for i, r in enumerate((10, 8, 6)):
        cx = x + w - 50 + (i - 1) * 6
        cy = y + 38 - i * 10
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(110, 110, 110))
    # flames on deck
    for fx, fh in ((x + 66, 34), (x + 96, 44), (x + 126, 30)):
        draw.polygon([(fx - 14, y + 58), (fx, y + 58 - fh),
                      (fx + 14, y + 58)], fill=(255, 120, 0))
        draw.polygon([(fx - 8, y + 58), (fx, y + 58 - fh + 14),
                      (fx + 8, y + 58)], fill=(255, 210, 0))


def draw_bank(draw, x, y, w, h):
    """Classical bank facade with columns, and a green RESTORED check."""
    # steps
    for i in range(3):
        draw.rectangle([x + 18 + i * 12, y + h - 30 + i * 8,
                        x + w - 18 - i * 12, y + h - 22 + i * 8],
                       fill=(150, 146, 134))
    # columns
    for i in range(4):
        cx = x + 52 + i * 64
        draw.rectangle([cx, y + 52, cx + 20, y + h - 30], fill=(228, 224, 212),
                       outline=INK, width=2)
    # pediment
    draw.polygon([(x + 30, y + 52), (x + w - 30, y + 52),
                  (x + w // 2, y + 14)], fill=(228, 224, 212),
                 outline=INK, width=2)
    draw.ellipse([x + w // 2 - 9, y + 30, x + w // 2 + 9, y + 48],
                 fill=GOLD, outline=INK, width=2)
    # door
    draw.rectangle([x + w // 2 - 26, y + h - 78, x + w // 2 + 26, y + h - 30],
                   fill=(60, 60, 60))
    # green check badge
    bx, by, br = x + w - 46, y + 30, 24
    draw.ellipse([bx - br, by - br, bx + br, by + br], fill=(34, 139, 34),
                 outline=(255, 255, 255), width=3)
    draw.line([(bx - 12, by), (bx - 3, by + 10), (bx + 13, by - 10)],
              fill=(255, 255, 255), width=5)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # outer double border
    d.rectangle([22, 22, W - 22, H - 22], outline=INK, width=3)
    d.rectangle([30, 30, W - 30, H - 30], outline=INK, width=1)

    # kicker
    y = 48
    y = centre(d, y, "THE DAY IN ONE PICTURE", font(SANS_BOLD, 21), RED)
    # masthead
    y = 76
    centre(d, y, "THE WORLD TODAY", font(SERIF_BLACK, 88), INK)
    # rules + dateline
    d.rectangle([52, 168, W - 52, 174], fill=INK)
    d.rectangle([52, 180, W - 52, 182], fill=INK)
    centre(d, 190, "TUESDAY  \u00b7  17 NOVEMBER 2026",
           font(SERIF_BOLD, 27), INK)

    # ---- lead panel ----
    d.rectangle([36, 232, W - 36, 512], fill=PANEL, outline=INK, width=2)
    # illustration band: long table, three flags
    band_y = 246
    d.rectangle([52, band_y + 96, W - 52, band_y + 118], fill=(120, 72, 32))
    d.rectangle([52, band_y + 118, W - 52, band_y + 124], fill=(90, 54, 24))
    for i, kind in enumerate(("CN", "US", "RU")):
        draw_flag(d, 300 + i * 160, band_y + 96, 74, 46, kind)
    # three chairs behind the table
    for cx in (330, 490, 650):
        d.rectangle([cx - 22, band_y + 96, cx + 22, band_y + 118],
                    fill=(70, 70, 70))
    # lead headline
    fnt, lines = fit_lines(d, "XI, TRUMP AND PUTIN TO MEET IN SHENZHEN",
                           SERIF_BLACK, 46, 940, 2)
    ly = 378
    for line in lines:
        ly = centre(d, ly, line, fnt, INK)
        ly += 4
    # sub-line (one line, kept inside the panel)
    fnt = font(SERIF, 21)
    sub = ("First trilateral summit confirmed for Thursday, "
           "at the APEC meetings in Shenzhen.")
    centre(d, ly + 8, sub, fnt, INK)

    # ---- three columns ----
    cols = [
        ("UKRAINE STRIKES KERCH BRIDGE AGAIN",
         "Traffic across the Crimea bridge halted; Russia hits two "
         "bridges in Kyiv.", draw_bridge),
        ("TANKERS ABLAZE NEAR HORMUZ",
         "Iran says tankers struck mines in the strait; its drones target "
         "a US radar site in Bahrain \u2014 Bahrain says all intercepted, "
         "no casualties.", draw_tanker),
        ("JPMORGAN OUTAGE FIXED",
         "Nationwide systems failure restored after hours; other banks "
         "and Zelle were also hit.", draw_bank),
    ]
    col_w, gap, top = 296, 24, 536
    for i, (head, cap, draw_fn) in enumerate(cols):
        x = 36 + i * (col_w + gap)
        d.rectangle([x, top, x + col_w, top + 3], fill=RED)
        draw_fn(d, x, top + 14, col_w, 150)
        fnt, lines = fit_lines(d, head, SERIF_BOLD, 27, col_w, 3)
        hy = top + 178
        for line in lines:
            d.text((x, hy), line, font=fnt, fill=INK)
            hy += fnt.size + 2
        fnt = font(SERIF, 18)
        for line in wrap(d, cap, fnt, col_w):
            d.text((x, hy + 6), line, font=fnt, fill=INK)
            hy += 24

    # ---- ticker ----
    d.rectangle([36, 912, W - 36, 964], fill=NAVY)
    tick = ("TRUMP AT QUAD TALKS IN MANILA    \u2022    MODI AT ASEAN "
            "SUMMIT    \u2022    BAHRAIN: DRONES INTERCEPTED")
    fnt = font(SANS_BOLD, 19)
    while d.textlength(tick, font=fnt) > 940 and fnt.size > 12:
        fnt = font(SANS_BOLD, fnt.size - 1)
    tw = d.textlength(tick, font=fnt)
    d.text(((W - tw) / 2, 930), tick, font=fnt, fill=(255, 255, 255))

    # footer
    centre(d, 972, "Wire reports  \u00b7  17 November 2026",
           font(SERIF, 14), GREY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, "PNG")
    print(f"saved {out} {img.size}")


if __name__ == "__main__":
    render()
