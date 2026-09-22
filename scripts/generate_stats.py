#!/usr/bin/env python3
"""
Self-hosted replacement for the pphat.top languages pie chart.

Fetches byte-weighted language usage across the user's own repos and
renders a bar list styled with the same Dracula palette and terminal
chrome as the ascii profile card and the tech-stack icons, instead of
pphat.top's own starfield-grid background.

Env vars:
  GITHUB_LOGIN   - github username (required)
  GITHUB_TOKEN   - token with public read access (recommended, avoids rate limits)
  OUT_PATH       - output svg path (default: assets/stats.svg)
"""

import os
import sys
import json
import urllib.request

from wrap_terminal import wrap_svg_string

LOGIN = os.environ.get("GITHUB_LOGIN", "vitoriaGoncalves08")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT_PATH = os.environ.get("OUT_PATH", "assets/stats.svg")

BG_COLOR = "#282a36"
TRACK_COLOR = "#3a3d55"
LABEL_COLOR = "#f8f8f2"
MUTED_COLOR = "#6272a4"

LANG_COLORS = {
    "JavaScript": "#F7DF1E", "TypeScript": "#3178C6", "Python": "#3776AB",
    "Java": "#ED8B00", "HTML": "#E34F26", "CSS": "#1572B6",
    "Vue": "#41B883", "PHP": "#777BB4", "C++": "#00599C", "C": "#555555",
    "C#": "#178600", "Go": "#00ADD8", "Ruby": "#CC342D", "Rust": "#DEA584",
    "Kotlin": "#7F52FF", "Swift": "#FA7343", "Shell": "#89E051",
    "Dockerfile": "#384D54", "Jupyter Notebook": "#DA5B0B",
}
DEFAULT_COLOR = "#bd93f9"

TOP_N = 8
LABEL_W = 150
BAR_W = 460
PCT_W = 55
ROW_H = 30
PAD = 24


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

    width = PAD * 2 + LABEL_W + BAR_W + PCT_W
    height = PAD * 2 + len(ranked) * ROW_H

    rows = []
    for i, (lang, byte_count) in enumerate(ranked):
        pct = byte_count / total_bytes * 100
        color = LANG_COLORS.get(lang, DEFAULT_COLOR)
        y = PAD + i * ROW_H
        fill_w = BAR_W * (byte_count / total_bytes)
        rows.append(f'''
  <g style="animation-delay:{i * 0.08:.2f}s" class="row">
    <circle cx="{PAD + 5}" cy="{y + 10}" r="5" fill="{color}" />
    <text x="{PAD + 18}" y="{y + 14}" font-family="Courier New, monospace" font-size="13" fill="{LABEL_COLOR}">{lang}</text>
    <rect x="{PAD + LABEL_W}" y="{y + 4}" width="{BAR_W}" height="12" rx="6" fill="{TRACK_COLOR}" />
    <rect x="{PAD + LABEL_W}" y="{y + 4}" width="{fill_w:.1f}" height="12" rx="6" fill="{color}" />
    <text x="{PAD + LABEL_W + BAR_W + 10}" y="{y + 14}" font-family="Courier New, monospace" font-size="12" fill="{MUTED_COLOR}">{pct:.1f}%</text>
  </g>''')

    return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <style>
    .row {{ animation: reveal 0.35s steps(1) forwards; opacity: 0; }}
    @keyframes reveal {{ to {{ opacity: 1; }} }}
  </style>
  <rect width="{width}" height="{height}" fill="{BG_COLOR}" />
  {"".join(rows)}
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
