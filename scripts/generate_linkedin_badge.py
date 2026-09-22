#!/usr/bin/env python3
"""
shields.io silently drops the LinkedIn logo from "for-the-badge" badges
(simple-icons removed it from shields' bundled set after a takedown
request), so this builds an equivalent badge locally, pulling the glyph
straight from the simple-icons npm package (still published there).
"""

import base64
import os
import urllib.request

OUT_PATH = os.environ.get("OUT_PATH", "assets/linkedin-badge.svg")
ICON_URL = "https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/linkedin.svg"
ICON_COLOR = "0A66C2"
WIDTH = 118


def build():
    with urllib.request.urlopen(ICON_URL, timeout=20) as r:
        icon_svg = r.read().decode("utf-8")
    icon_svg = icon_svg.replace("<svg ", f'<svg fill="#{ICON_COLOR}" ', 1)
    b64 = base64.b64encode(icon_svg.encode("utf-8")).decode("ascii")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="28" role="img" aria-label="LINKEDIN">
  <title>LINKEDIN</title>
  <rect width="{WIDTH}" height="28" fill="#000000"/>
  <image x="9" y="7" width="14" height="14" href="data:image/svg+xml;base64,{b64}"/>
  <text x="32" y="18.5" font-family="Verdana, Geneva, DejaVu Sans, sans-serif" font-size="10.5" font-weight="bold" letter-spacing="0.6" fill="#ffffff">LINKEDIN</text>
</svg>
'''
    os.makedirs(os.path.dirname(OUT_PATH) or ".", exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    build()
