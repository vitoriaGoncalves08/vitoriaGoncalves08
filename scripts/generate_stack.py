#!/usr/bin/env python3
"""
Builds a self-contained, floating "Tech Stack & Tools" SVG.

Each technology's official devicon glyph is embedded inline (no external
network requests at render time) inside a soft, brand-tinted rounded card.
Every card bobs up and down on a staggered delay, producing the same
"wave" effect used by icon services like stats.pphat.top, but with full
control over which technologies are included.

Run locally (not a scheduled Action, the stack rarely changes):
    python scripts/generate_stack.py
"""

import os
import re
import urllib.request

OUT_PATH = os.environ.get("OUT_PATH", "assets/stack.svg")

# (devicon slug, file variant, brand color used for the card tint)
ICONS = [
    ("html5", "original", "#E34F26"),
    ("css3", "original", "#1572B6"),
    ("javascript", "original", "#F7DF1E"),
    ("typescript", "original", "#3178C6"),
    ("react", "original", "#61DAFB"),
    ("angularjs", "original", "#DD0031"),
    ("java", "original", "#ED8B00"),
    ("spring", "original", "#6DB33F"),
    ("amazonwebservices", "original-wordmark", "#FF9900"),
    ("git", "original", "#F05032"),
    ("docker", "original", "#2496ED"),
    ("python", "original", "#3776AB"),
]

CARD = 90
GAP = 18
PAD = 24
COLUMNS = 6
ICON_SIZE = 50


def fetch_icon(slug, variant):
    url = f"https://raw.githubusercontent.com/devicons/devicon/master/icons/{slug}/{slug}-{variant}.svg"
    with urllib.request.urlopen(url, timeout=20) as r:
        return r.read().decode("utf-8")


def inner_and_viewbox(svg_text):
    vb_match = re.search(r'viewBox="([^"]+)"', svg_text)
    view_box = vb_match.group(1) if vb_match else "0 0 128 128"
    inner = re.sub(r"^.*?<svg[^>]*>", "", svg_text, flags=re.S)
    inner = re.sub(r"</svg>\s*$", "", inner.strip(), flags=re.S)
    return inner, view_box


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def build():
    rows = -(-len(ICONS) // COLUMNS)
    width = COLUMNS * CARD + (COLUMNS - 1) * GAP + 2 * PAD
    height = rows * CARD + (rows - 1) * GAP + 2 * PAD

    cards = []
    for i, (slug, variant, color) in enumerate(ICONS):
        col = i % COLUMNS
        row = i // COLUMNS
        x = PAD + col * (CARD + GAP)
        y = PAD + row * (CARD + GAP)

        svg_text = fetch_icon(slug, variant)
        inner, view_box = inner_and_viewbox(svg_text)
        r, g, b = hex_to_rgb(color)
        icon_offset = (CARD - ICON_SIZE) / 2
        delay = round(i * 0.12, 2)

        cards.append(f'''
  <g transform="translate({x},{y})">
    <g class="float" style="animation-delay:{delay}s">
      <rect width="{CARD}" height="{CARD}" rx="20" fill="rgba({r},{g},{b},0.14)" />
      <svg x="{icon_offset:.1f}" y="{icon_offset:.1f}" width="{ICON_SIZE}" height="{ICON_SIZE}" viewBox="{view_box}">
        {inner}
      </svg>
    </g>
  </g>''')

    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <style>
    .float {{ animation: floaty 2.6s ease-in-out infinite; }}
    @keyframes floaty {{
      0%, 100% {{ transform: translateY(0px); }}
      50% {{ transform: translateY(-10px); }}
    }}
  </style>
  {"".join(cards)}
</svg>
'''
    os.makedirs(os.path.dirname(OUT_PATH) or ".", exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    build()
