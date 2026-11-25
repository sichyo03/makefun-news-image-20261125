#!/usr/bin/env python3
"""Draw the 25 November 2026 world-news front page for the make.fun bounty.

An illustrated newspaper front page (flat, original art) rendered with PIL:
masthead "THE WORLD", the date WEDNESDAY, 25 NOVEMBER 2026, one lead story
(illustration + headline) and a 2x2 grid of four more stories, each with a
simple icon illustration, a short headline and a one-line caption.

Output: entry.png, 1024x1024, beside this file.
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (26, 24, 22)
MUTED = (96, 90, 80)
RULE = (26, 24, 22)
ACCENT = (178, 34, 34)      # deep red for the lead kicker
SEA = (46, 96, 140)
SEA_DARK = (32, 70, 108)
SKY = (245, 197, 120)       # warm dawn sky for the lead panel
HULL = (52, 54, 60)
DECK = (120, 124, 132)
MINE = (30, 30, 32)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_COND = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_center(draw, cx, y, s, fnt, fill=INK):
    bbox = draw.textbbox((0, 0), s, font=fnt)
    w = bbox[2] - bbox[0]
    draw.text((cx - w / 2 - bbox[0], y), s, font=fnt, fill=fill)
    return bbox[3] - bbox[1]


def wrap(draw, s, fnt, max_w):
    words, lines, cur = s.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textbbox((0, 0), trial, font=fnt)[2] <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_tanker(draw, x0, y0, x1, y1):
    """Lead illustration: an oil tanker and a naval mine in a strait."""
    # sky and sea bands
    draw.rectangle([x0, y0, x1, y0 + (y1 - y0) * 0.42], fill=SKY)
    draw.rectangle([x0, y0 + (y1 - y0) * 0.42, x1, y1], fill=SEA)
    # low sun
    sx, sy, sr = x0 + (x1 - x0) * 0.82, y0 + (y1 - y0) * 0.20, 30
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(240, 140, 60))
    # tanker hull (side view, long flat hull with a bow)
    sea_y = y0 + (y1 - y0) * 0.42
    hull_top = sea_y + 26
    hull_bot = hull_top + 44
    bow_x = x0 + 60
    stern_x = x1 - 120
    draw.polygon([(bow_x, hull_top), (stern_x, hull_top), (stern_x + 46, hull_top + 14),
                  (stern_x + 30, hull_bot), (bow_x + 26, hull_bot), (bow_x, hull_top + 16)],
                 fill=HULL)
    draw.rectangle([bow_x + 30, hull_top - 12, stern_x - 60, hull_top], fill=DECK)
    # superstructure block + funnel
    draw.rectangle([stern_x - 120, hull_top - 52, stern_x - 40, hull_top - 12], fill=(200, 202, 208))
    draw.rectangle([stern_x - 104, hull_top - 70, stern_x - 76, hull_top - 52], fill=(90, 92, 98))
    # containers on deck
    for i, col in enumerate([(178, 60, 50), (60, 110, 150), (70, 150, 90)]):
        cx = bow_x + 60 + i * 86
        draw.rectangle([cx, hull_top - 38, cx + 74, hull_top - 12], fill=col)
    # wake
    for i in range(4):
        wy = hull_bot + 8 + i * 9
        draw.line([bow_x + 10, wy, bow_x + 90 + i * 26, wy], fill=(220, 232, 244), width=3)
    # naval mine (spiked ball) near the bow, half submerged
    mx, my, mr = bow_x - 6, hull_bot - 6, 24
    for a in range(0, 360, 45):
        rad = math.radians(a)
        draw.line([mx, my, mx + math.cos(rad) * (mr + 12), my + math.sin(rad) * (mr + 12)],
                  fill=MINE, width=5)
    draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=MINE)
    draw.ellipse([mx - 7, my - 7, mx + 7, my + 7], fill=(120, 120, 126))


def icon_warship(draw, cx, cy, s):
    """Warship with a small drone above it."""
    sea_y = cy + s * 0.28
    draw.rectangle([cx - s, sea_y, cx + s, cy + s * 0.72], fill=SEA)
    draw.polygon([(cx - s * 0.8, sea_y - 6), (cx + s * 0.8, sea_y - 6),
                  (cx + s * 0.62, sea_y + 18), (cx - s * 0.62, sea_y + 18)], fill=HULL)
    draw.rectangle([cx - s * 0.30, sea_y - 26, cx + s * 0.10, sea_y - 6], fill=DECK)
    draw.rectangle([cx - s * 0.12, sea_y - 46, cx - s * 0.02, sea_y - 26], fill=(90, 92, 98))
    draw.line([cx + s * 0.35, sea_y - 6, cx + s * 0.55, sea_y - 34], fill=HULL, width=5)  # gun
    # drone
    dx, dy = cx + s * 0.55, cy - s * 0.55
    draw.ellipse([dx - 10, dy - 6, dx + 10, dy + 6], fill=MINE)
    for ox, oy in [(-16, -10), (16, -10), (-16, 10), (16, 10)]:
        draw.line([dx, dy, dx + ox, dy + oy], fill=MINE, width=3)
        draw.ellipse([dx + ox - 5, dy + oy - 3, dx + ox + 5, dy + oy + 3], fill=(120, 120, 126))


def icon_chip(draw, cx, cy, s):
    """Microchip with a downward market arrow."""
    half = s * 0.55
    draw.rectangle([cx - half, cy - half, cx + half, cy + half], fill=(44, 62, 80))
    draw.rectangle([cx - half * 0.55, cy - half * 0.55, cx + half * 0.55, cy + half * 0.55],
                   fill=(86, 130, 168))
    for i in range(-2, 3):
        off = i * s * 0.22
        draw.line([cx + off, cy - half, cx + off, cy - half - 12], fill=(44, 62, 80), width=4)
        draw.line([cx + off, cy + half, cx + off, cy + half + 12], fill=(44, 62, 80), width=4)
        draw.line([cx - half, cy + off, cx - half - 12, cy + off], fill=(44, 62, 80), width=4)
        draw.line([cx + half, cy + off, cx + half + 12, cy + off], fill=(44, 62, 80), width=4)
    # falling arrow across the chip
    draw.line([cx - half * 0.8, cy - half * 0.45, cx - half * 0.1, cy + half * 0.05,
               cx + half * 0.25, cy - half * 0.15, cx + half * 0.85, cy + half * 0.55],
              fill=(200, 50, 45), width=7, joint="curve")
    ax, ay = cx + half * 0.85, cy + half * 0.55
    draw.polygon([(ax, ay), (ax - 18, ay - 2), (ax - 4, ay - 18)], fill=(200, 50, 45))


def icon_station(draw, cx, cy, s):
    """Space station with a small capsule approaching."""
    draw.rectangle([cx - s * 0.85, cy - 8, cx + s * 0.85, cy + 8], fill=(150, 156, 166))
    draw.rectangle([cx - s * 0.85, cy - s * 0.32, cx - s * 0.30, cy + s * 0.32], fill=(46, 96, 140))
    draw.rectangle([cx + s * 0.30, cy - s * 0.32, cx + s * 0.85, cy + s * 0.32], fill=(46, 96, 140))
    draw.rectangle([cx - 16, cy - 22, cx + 16, cy + 22], fill=(210, 212, 218))
    draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(46, 96, 140))
    # capsule below-right
    kx, ky = cx + s * 0.35, cy + s * 0.55
    draw.polygon([(kx - 16, ky + 12), (kx + 16, ky + 12), (kx + 9, ky - 14), (kx - 9, ky - 14)],
                 fill=(200, 202, 208))
    draw.polygon([(kx - 9, ky + 12), (kx + 9, ky + 12), (kx, ky + 28)], fill=(240, 140, 60))
    # stars
    for sx, sy in [(cx - s * 0.7, cy - s * 0.6), (cx + s * 0.6, cy - s * 0.65),
                   (cx - s * 0.15, cy - s * 0.75)]:
        draw.line([sx - 6, sy, sx + 6, sy], fill=(120, 120, 126), width=3)
        draw.line([sx, sy - 6, sx, sy + 6], fill=(120, 120, 126), width=3)


def icon_trophy(draw, cx, cy, s):
    """Trophy cup with a football beside it."""
    top_y = cy - s * 0.55
    draw.polygon([(cx - s * 0.42, top_y), (cx + s * 0.42, top_y),
                  (cx + s * 0.28, cy + s * 0.05), (cx - s * 0.28, cy + s * 0.05)],
                 fill=(226, 178, 60))
    draw.arc([cx - s * 0.62, top_y + 2, cx - s * 0.30, top_y + s * 0.42], 90, 270,
             fill=(196, 148, 40), width=6)
    draw.arc([cx + s * 0.30, top_y + 2, cx + s * 0.62, top_y + s * 0.42], 270, 90,
             fill=(196, 148, 40), width=6)
    draw.rectangle([cx - 7, cy + s * 0.05, cx + 7, cy + s * 0.30], fill=(196, 148, 40))
    draw.rectangle([cx - s * 0.30, cy + s * 0.30, cx + s * 0.30, cy + s * 0.42],
                   fill=(120, 84, 30))
    # football
    fx, fy, fr = cx + s * 0.55, cy + s * 0.35, s * 0.26
    draw.ellipse([fx - fr, fy - fr, fx + fr, fy + fr], fill=(250, 250, 250), outline=INK, width=3)
    draw.polygon([(fx, fy - fr * 0.45), (fx + fr * 0.42, fy - fr * 0.14),
                  (fx + fr * 0.26, fy + fr * 0.38), (fx - fr * 0.26, fy + fr * 0.38),
                  (fx - fr * 0.42, fy - fr * 0.14)], fill=INK)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    margin = 44
    cx = W // 2

    # --- masthead ---
    y = 26
    d.line([margin, y, W - margin, y], fill=RULE, width=2)
    y += 12
    h = text_center(d, cx, y, "THE WORLD", font(SERIF_BOLD, 78))
    y += h + 18
    h = text_center(d, cx, y, "WEDNESDAY, 25 NOVEMBER 2026", font(SANS_BOLD, 34))
    y += h + 12
    d.line([margin, y, W - margin, y], fill=RULE, width=5)
    y += 8
    d.line([margin, y, W - margin, y], fill=RULE, width=2)
    y += 16

    # --- lead story ---
    lead_h = 330
    d.text((margin, y), "THE LEAD", font=font(SANS_BOLD, 22), fill=ACCENT)
    y += 28
    panel = [margin, y, W - margin, y + 140]
    draw_tanker(d, *panel)
    y += 150
    lead_head = "TANKERS HIT MINES IN STRAIT OF HORMUZ"
    for line in wrap(d, lead_head, font(SANS_BOLD, 42), W - 2 * margin):
        d.text((margin, y), line, font=font(SANS_BOLD, 42), fill=INK)
        y += 47
    y += 2
    lead_cap = "Iran's Revolutionary Guards say two oil tankers struck mines in the strait."
    for line in wrap(d, lead_cap, font(SANS, 24), W - 2 * margin):
        d.text((margin, y), line, font=font(SANS, 24), fill=MUTED)
        y += 29
    y += 12
    d.line([margin, y, W - margin, y], fill=RULE, width=2)
    y += 14

    # --- 2x2 grid ---
    stories = [
        (icon_warship, "UKRAINE SINKS RUSSIAN WARSHIP",
         "Naval drones sink the corvette Merkury in a Libyan port."),
        (icon_chip, "AI STOCKS TUMBLE; NVIDIA FALLS",
         "Nikkei drops 2.8% as AI boom doubts hit markets."),
        (icon_station, "PAKISTAN'S FIRST ASTRONAUT IN ORBIT",
         "Reaches China's space station."),
        (icon_trophy, "SENEGAL REGAIN AFRICA CUP",
         "Senegal take back the Africa Cup of Nations title."),
    ]
    col_w = (W - 2 * margin - 24) // 2
    row_h = 212
    for idx, (icon, head, cap) in enumerate(stories):
        col, row = idx % 2, idx // 2
        gx = margin + col * (col_w + 24)
        gy = y + row * row_h
        # icon area
        icon(d, gx + col_w // 2, gy + 56, 58)
        ty = gy + 106
        for line in wrap(d, head, font(SANS_COND, 27), col_w):
            text_center(d, gx + col_w // 2, ty, line, font(SANS_COND, 27))
            ty += 31
        for line in wrap(d, cap, font(SANS, 21), col_w - 8):
            text_center(d, gx + col_w // 2, ty, line, font(SANS, 21), fill=MUTED)
            ty += 25
    y += 2 * row_h + 8

    # --- footer ---
    d.line([margin, y, W - margin, y], fill=RULE, width=2)
    y += 12
    text_center(d, cx, y, "Five stories that shaped the day", font(SANS, 22), fill=MUTED)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
