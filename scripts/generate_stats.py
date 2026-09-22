#!/usr/bin/env python3
"""
Self-hosted replacement for the pphat.top languages pie chart.

Fetches byte-weighted language usage across the user's own repos and
renders an animated donut chart + legend, styled with the same Dracula
palette and terminal chrome as the ascii profile card and the tech-stack
icons, instead of pphat.top's own starfield-grid background.

Env vars:
  GITHUB_LOGIN   - github username (required)
  GITHUB_TOKEN   - token with public read access (recommended, avoids rate limits)
  OUT_PATH       - output svg path (default: assets/stats.svg)
"""

import os
import sys
import json
import math
import urllib.request

from wrap_terminal import wrap_svg_string

LOGIN = os.environ.get("GITHUB_LOGIN", "vitoriaGoncalves08")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT_PATH = os.environ.get("OUT_PATH", "assets/stats.svg")

BG_COLOR = "#282a36"
LABEL_COLOR = "#f8f8f2"
MUTED_COLOR = "#6272a4"
ACCENT = "#bd93f9"

LANG_COLORS = {
    "JavaScript": "#F7DF1E", "TypeScript": "#3178C6", "Python": "#3776AB",
    "Java": "#ED8B00", "HTML": "#E34F26", "CSS": "#1572B6",
    "Vue": "#41B883", "PHP": "#777BB4", "C++": "#00599C", "C": "#555555",
    "C#": "#178600", "Go": "#00ADD8", "Ruby": "#CC342D", "Rust": "#DEA584",
    "Kotlin": "#7F52FF", "Swift": "#FA7343", "Shell": "#89E051",
    "Dockerfile": "#384D54", "Jupyter Notebook": "#DA5B0B", "Hack": "#878787",
}
DEFAULT_COLOR = "#bd93f9"

TOP_N = 8
PAD = 28
R = 74
SW = 28
SPIN_DUR = 26
LEGEND_ROW_H = 26
LEGEND_W = 230
GAP = 40


def api_get(url):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_language_totals(login):
    repos = api_get(f"https://api.github.com/users/{login}/repos?per_page=100&type=owner")
    totals = {}
    for repo in repos:
        if repo.get("fork"):
            continue
        try:
            langs = api_get(repo["languages_url"])
        except Exception as e:
            print(f"warning: could not fetch languages for {repo.get('name')}: {e}", file=sys.stderr)
            continue
        for lang, byte_count in langs.items():
            totals[lang] = totals.get(lang, 0) + byte_count
    return totals


def build_chart_svg(totals):
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:TOP_N]
    total_bytes = sum(v for _, v in ranked) or 1

    donut_box = 2 * (R + SW / 2)
    legend_h = len(ranked) * LEGEND_ROW_H
    content_h = max(donut_box, legend_h)
    width = PAD * 2 + donut_box + GAP + LEGEND_W
    height = PAD * 2 + content_h

    cx = PAD + R + SW / 2
    cy = PAD + content_h / 2
    circumference = 2 * math.pi * R

    segments = []
    cumulative = 0.0
    for i, (lang, byte_count) in enumerate(ranked):
        frac = byte_count / total_bytes
        seg_len = frac * circumference
        color = LANG_COLORS.get(lang, DEFAULT_COLOR)
        delay = round(i * 0.12, 2)
        segments.append(f'''
    <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R}" fill="none" stroke="{color}" stroke-width="{SW}"
            stroke-dasharray="{seg_len:.2f} {circumference - seg_len:.2f}"
            stroke-dashoffset="{-cumulative:.2f}"
            class="segment" style="animation-delay:{delay}s" />''')
        cumulative += seg_len

    legend_x = PAD + donut_box + GAP
    legend_top = PAD + (content_h - legend_h) / 2
    legend_rows = []
    for i, (lang, byte_count) in enumerate(ranked):
        pct = byte_count / total_bytes * 100
        color = LANG_COLORS.get(lang, DEFAULT_COLOR)
        y = legend_top + i * LEGEND_ROW_H
        delay = round(0.3 + i * 0.1, 2)
        legend_rows.append(f'''
  <g class="legend-row" style="animation-delay:{delay}s">
    <circle cx="{legend_x + 5}" cy="{y + 9}" r="5" fill="{color}" />
    <text x="{legend_x + 18}" y="{y + 13}" font-family="Courier New, monospace" font-size="13" fill="{LABEL_COLOR}">{lang}</text>
    <text x="{legend_x + LEGEND_W}" y="{y + 13}" text-anchor="end" font-family="Courier New, monospace" font-size="12" fill="{MUTED_COLOR}">{pct:.1f}%</text>
  </g>''')

    return f'''<svg width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}" xmlns="http://www.w3.org/2000/svg">
  <style>
    .segment {{
      animation: drawIn 0.6s ease-out both;
    }}
    @keyframes drawIn {{
      from {{ opacity: 0; stroke-width: 0; }}
      to {{ opacity: 1; stroke-width: {SW}; }}
    }}
    .legend-row {{ animation: reveal 0.35s steps(1) forwards; opacity: 0; }}
    @keyframes reveal {{ to {{ opacity: 1; }} }}
    .center-label {{ font-family: Courier New, monospace; fill: {ACCENT}; text-anchor: middle; }}
    #spinner {{
      transform-origin: {cx:.1f}px {cy:.1f}px;
      animation: spin {SPIN_DUR}s linear infinite;
    }}
    @keyframes spin {{
      from {{ transform: rotate(-90deg); }}
      to {{ transform: rotate(270deg); }}
    }}
  </style>
  <rect width="{width:.0f}" height="{height:.0f}" fill="{BG_COLOR}" />
  <g id="spinner">
    {"".join(segments)}
  </g>
  <text x="{cx:.1f}" y="{cy - 4:.1f}" class="center-label" font-size="12" font-weight="bold">TOP {len(ranked)}</text>
  <text x="{cx:.1f}" y="{cy + 14:.1f}" class="center-label" font-size="10" fill="{MUTED_COLOR}">LANGUAGES</text>
  {"".join(legend_rows)}
</svg>
'''


def main():
    totals = {}
    try:
        totals = fetch_language_totals(LOGIN)
    except Exception as e:
        print(f"warning: failed to fetch language stats: {e}", file=sys.stderr)

    if not totals:
        totals = {"N/A": 1}

    raw_svg = build_chart_svg(totals)
    wrapped = wrap_svg_string(raw_svg, f"{LOGIN}@github: status")

    os.makedirs(os.path.dirname(OUT_PATH) or ".", exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(wrapped)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
