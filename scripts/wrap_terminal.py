#!/usr/bin/env python3
"""
Wraps an existing SVG (e.g. the pacman contribution graph) in the same
dark terminal-window chrome (title bar + traffic-light dots) used by the
ascii profile card, so every generated asset in the README shares one
visual language.

Usage:
    python scripts/wrap_terminal.py <input.svg> <output.svg> "<title text>" [scale]

`scale` (default 1.0) enlarges the wrapped graphic without touching its
own generator - e.g. 1.15 renders it 15% bigger inside the window.
"""

import re
import sys

BG_COLOR = "#282a36"
TITLEBAR_COLOR = "#21222c"
TITLE_TEXT_COLOR = "#6272a4"

PAD = 16
TITLEBAR_H = 34
RADIUS = 10


def wrap(input_path, output_path, title, scale=1.0):
    with open(input_path, "r", encoding="utf-8") as f:
        original = f.read()

    root_match = re.search(r"<svg[^>]*>", original)
    if not root_match:
        raise ValueError(f"no <svg> root tag found in {input_path}")
    root_tag = root_match.group(0)

    width_match = re.search(r'width="([\d.]+)', root_tag)
    height_match = re.search(r'height="([\d.]+)', root_tag)
    if not (width_match and height_match):
        raise ValueError(f"could not read width/height from {input_path}")
    orig_w = float(width_match.group(1))
    orig_h = float(height_match.group(1))
    inner_w = orig_w * scale
    inner_h = orig_h * scale

    inner_content = original[root_match.end():]
    inner_content = re.sub(r"</svg>\s*$", "", inner_content.strip(), flags=re.S)

    total_w = inner_w + 2 * PAD
    total_h = inner_h + 2 * PAD + TITLEBAR_H

    chrome = f'''<svg width="{total_w:.0f}" height="{total_h:.0f}" viewBox="0 0 {total_w:.0f} {total_h:.0f}" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="{total_w:.0f}" height="{total_h:.0f}" rx="{RADIUS}" fill="{BG_COLOR}" />
  <path d="M0,{RADIUS} a{RADIUS},{RADIUS} 0 0 1 {RADIUS},-{RADIUS} h{total_w - 2*RADIUS:.0f} a{RADIUS},{RADIUS} 0 0 1 {RADIUS},{RADIUS} v{TITLEBAR_H - RADIUS:.0f} h-{total_w:.0f} z"
        fill="{TITLEBAR_COLOR}" />
  <circle cx="24" cy="{TITLEBAR_H/2:.0f}" r="6" fill="#ff5555" />
  <circle cx="46" cy="{TITLEBAR_H/2:.0f}" r="6" fill="#f1fa8c" />
  <circle cx="68" cy="{TITLEBAR_H/2:.0f}" r="6" fill="#50fa7b" />
  <text x="{total_w/2:.0f}" y="{TITLEBAR_H/2 + 5:.0f}" text-anchor="middle"
        font-family="Courier New, monospace" font-size="13" fill="{TITLE_TEXT_COLOR}">{title}</text>
  <line x1="0" y1="{TITLEBAR_H}" x2="{total_w:.0f}" y2="{TITLEBAR_H}" stroke="#3a3d55" stroke-width="1" />
  <svg x="{PAD}" y="{PAD + TITLEBAR_H}" width="{inner_w:.0f}" height="{inner_h:.0f}" viewBox="0 0 {orig_w:.0f} {orig_h:.0f}">
    {inner_content}
  </svg>
</svg>
'''

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(chrome)
    print(f"wrapped {input_path} -> {output_path}")


if __name__ == "__main__":
    if len(sys.argv) not in (4, 5):
        print("usage: wrap_terminal.py <input.svg> <output.svg> <title> [scale]", file=sys.stderr)
        sys.exit(1)
    scale_arg = float(sys.argv[4]) if len(sys.argv) == 5 else 1.0
    wrap(sys.argv[1], sys.argv[2], sys.argv[3], scale_arg)
