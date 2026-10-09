#!/usr/bin/env python3
"""Create a self-contained animated GitHub-style contribution heatmap."""

from __future__ import annotations

import datetime as dt
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data" / "contributions.json"


def read_data(user: str) -> tuple[list[dict], int]:
    if SNAPSHOT.exists():
        snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        if snapshot.get("username", "").lower() == user.lower() and snapshot.get("days"):
            return snapshot["days"], snapshot.get("total_contributions", 0)

    try:
        url = f"https://github-contributions-api.jogruber.de/v4/{user}?y=last"
        req = urllib.request.Request(url, headers={"User-Agent": "OmkarYelsange-github-profile/1.0"})
        with urllib.request.urlopen(req, timeout=25) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return payload["contributions"], payload["total"]["lastYear"]
    except Exception:
        return [], 0


def render(days: list[dict], total: int) -> str:
    cell, gap, left, top = 13, 3, 34, 28
    colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

    if not days:
        return '''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="160" viewBox="0 0 860 160">
<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>
<rect width="860" height="160" rx="12" fill="url(#bg)"/><rect x="0.5" y="0.5" width="859" height="159" rx="12" fill="none" stroke="#30363d"/>
<text x="40" y="55" fill="#7d8590" font-size="15" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">omkar@github: ~/contributions</text>
<text x="40" y="92" fill="#e6edf3" font-size="22" font-weight="700" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">Waiting for the first Actions refresh</text>
<text x="40" y="123" fill="#7d8590" font-size="14" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">Run the workflow once to replace this placeholder with real data.</text>
</svg>'''

    columns = (len(days) + 6) // 7
    width = left + columns * (cell + gap) + 12
    height = top + 7 * (cell + gap) + 42
    reveal_span = max(columns - 1 + 6 * 0.65, 1)

    labels = []
    seen = set()
    for i, day in enumerate(days):
        date = dt.date.fromisoformat(day["date"])
        if date.day <= 7 and (date.year, date.month) not in seen:
            seen.add((date.year, date.month))
            week = i // 7
            labels.append(f'<text class="label" x="{left + week*(cell+gap)}" y="15">{date.strftime("%b")}</text>')

    for row, name in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        y = top + row * (cell + gap) + cell - 2
        labels.append(f'<text class="label" x="2" y="{y}">{name}</text>')

    rects = []
    for i, day in enumerate(days):
        week, row = i // 7, i % 7
        x, y = left + week * (cell + gap), top + row * (cell + gap)
        delay = ((week + row * 0.65) / reveal_span) * 4.0
        level = max(0, min(4, int(day.get("level", 0))))
        count = day["count"]
        plural = "" if count == 1 else "s"
        rects.append(
            f'<rect class="cell" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2.5" '
            f'fill="{colors[level]}" style="animation-delay:{delay:.3f}s"><title>{day["date"]}: {count} contribution{plural}</title></rect>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">
<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>
<style>.label{{fill:#7d8590;font-size:11px;font-weight:600}}.cell{{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .5s ease-out both}}@keyframes pop{{0%{{opacity:0;transform:scale(.25)}}60%{{opacity:1;transform:scale(1.12)}}100%{{opacity:1;transform:scale(1)}}}}@media (prefers-reduced-motion:reduce){{.cell{{opacity:1;animation:none}}}}</style>
<rect width="{width}" height="{height}" rx="12" fill="url(#bg)"/><rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="12" fill="none" stroke="#30363d"/>
<text x="{width/2:.1f}" y="25" text-anchor="middle" fill="#7d8590" font-size="12">omkar@github: ~/contributions --graph</text>
{''.join(labels)}{''.join(rects)}
<text x="{left}" y="{height-8}" fill="#e6edf3" font-size="14" font-weight="700">{total:,} contributions in the last year</text>
</svg>'''


def main() -> None:
    user = sys.argv[1] if len(sys.argv) > 1 else "OmkarYelsange"
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "contrib-heatmap.svg"
    days, total = read_data(user)
    output.write_text(render(days, total), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
