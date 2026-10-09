#!/usr/bin/env python3
"""Render the animated terminal statistics card from contributions.json."""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "contributions.json"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "stats.svg"
W, H = 840, 880
PAD, TITLE_H, GAP, TILE_H = 20, 30, 16, 145
TILE_W = (W - 2 * PAD - GAP) / 2


def dlabel(value):
    def dlabel(value):
    	if not value:
        	return "—"
    	parsed = dt.date.fromisoformat(value)
    	return f"{parsed.strftime('%b')} {parsed.day}"


def span(item):
    return "—" if not item.get("length") else f'{dlabel(item.get("start"))} – {dlabel(item.get("end"))}'


def fallback():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs><rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/><rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="#30363d"/><line x1="0" y1="{TITLE_H}" x2="{W}" y2="{TITLE_H}" stroke="#30363d"/><text x="{W/2}" y="20" text-anchor="middle" fill="#7d8590" font-size="12" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">omkar@github: ~$ ./stats.sh</text><text x="42" y="125" fill="#e6edf3" font-size="30" font-weight="700" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">Profile stats</text><text x="42" y="165" fill="#7d8590" font-size="18" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">Waiting for GitHub Actions to generate data…</text></svg>'''


def render(data):
    days = data.get("days", [])
    if not days:
        return fallback()

    cur, lng, best = data.get("current_streak", {}), data.get("longest_streak", {}), data.get("best_day", {})
    active, total_days = data.get("active_days", 0), len(days)
    avg = float(data.get("avg_per_active_day", 0))
    tiles = [
        ("current streak", cur.get("length", 0), " days", span(cur), "#39d353"),
        ("longest streak", lng.get("length", 0), " days", span(lng), "#e6edf3"),
        ("contributions", data.get("total_contributions", 0), "", "in the last year", "#e6edf3"),
        ("active days", active, f" / {total_days}", f"{active/total_days:.0%} of the year", "#e6edf3"),
        ("best day", best.get("count", 0), "", dlabel(best.get("date")), "#e6edf3"),
        ("avg / active day", avg, "", "contributions", "#e6edf3"),
    ]

    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"><defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs><style>.tile{{opacity:0;animation:slide .45s ease-out both}}.bar{{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .6s ease-out both}}@keyframes slide{{0%{{opacity:0;transform:translateY(12px)}}100%{{opacity:1;transform:translateY(0)}}}}@keyframes grow{{to{{transform:scaleY(1)}}}}@media (prefers-reduced-motion:reduce){{.tile,.bar{{opacity:1;transform:none;animation:none}}}}</style><rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/><rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="#30363d"/><line x1="0" y1="{TITLE_H}" x2="{W}" y2="{TITLE_H}" stroke="#30363d"/><text x="{W/2}" y="20" text-anchor="middle" fill="#7d8590" font-size="12">omkar@github: ~$ ./stats.sh</text>''']

    top = TITLE_H + 24
    for i, (label, value, suffix, caption, accent) in enumerate(tiles):
        col, row = i % 2, i // 2
        x, y = PAD + col * (TILE_W + GAP), top + row * (TILE_H + GAP)
        shown = f"{value:,.1f}" if isinstance(value, float) else f"{int(value):,}"
        parts.append(f'''<g class="tile" style="animation-delay:{i*0.14:.2f}s"><rect x="{x:.1f}" y="{y}" width="{TILE_W:.1f}" height="{TILE_H}" rx="10" fill="#161b22" stroke="#30363d"/><text x="{x+24:.1f}" y="{y+39}" fill="#7d8590" font-size="20">$ {label}</text><text x="{x+24:.1f}" y="{y+99}" fill="{accent}" font-size="50" font-weight="700">{shown}<tspan font-size="22" font-weight="400" fill="#7d8590">{suffix}</tspan></text><text x="{x+24:.1f}" y="{y+128}" fill="#7d8590" font-size="17">{caption}</text></g>''')

    monthly = data.get("monthly", [])
    chart_top, chart_h = top + 3 * TILE_H + 2 * GAP + 20, H - (top + 3 * TILE_H + 2 * GAP + 20) - PAD
    parts.append(f'''<g class="tile" style="animation-delay:.9s"><rect x="{PAD}" y="{chart_top}" width="{W-2*PAD}" height="{chart_h}" rx="10" fill="#161b22" stroke="#30363d"/><text x="{PAD+24}" y="{chart_top+38}" fill="#7d8590" font-size="20">$ contributions / month</text></g>''')

    if monthly:
        pl, pr, pt, pb = PAD + 32, W - PAD - 32, chart_top + 62, chart_top + chart_h - 42
        slot = (pr - pl) / len(monthly)
        bw, peak = max(2.0, slot * 0.62), max(item["total"] for item in monthly) or 1
        for i, item in enumerate(monthly):
            bh = max(2.0, (pb - pt) * item["total"] / peak)
            bx, by = pl + i * slot + (slot - bw) / 2, pb - bh
            parts.append(f'<rect class="bar" x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="3" fill="#26a641" style="animation-delay:{1.15+i*0.05:.2f}s"/>')
            month = dt.date.fromisoformat(item["month"] + "-01").strftime("%b")[0]
            parts.append(f'<text x="{bx+bw/2:.1f}" y="{pb+24}" fill="#7d8590" font-size="15" text-anchor="middle">{month}</text>')

    parts.append("</svg>")
    return "".join(parts)


def main():
    data = json.loads(SRC.read_text(encoding="utf-8")) if SRC.exists() else {}
    OUT.write_text(render(data), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
