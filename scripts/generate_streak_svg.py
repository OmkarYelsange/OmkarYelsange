#!/usr/bin/env python3
'''Create a self-contained animated GitHub-style contribution heatmap.'''

from __future__ import annotations

import datetime as dt
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data" / "contributions.json"


def read_data(user: str) -> tuple[list[dict], int]:
    '''Read the local snapshot, falling back to the public contribution API.'''
    if SNAPSHOT.exists():
        try:
            snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
            if (
                snapshot.get("username", "").lower() == user.lower()
                and snapshot.get("days")
            ):
                return snapshot["days"], int(snapshot.get("total_contributions", 0))
        except (OSError, json.JSONDecodeError, AttributeError, TypeError):
            pass

    url = f"https://github-contributions-api.jogruber.de/v4/{user}?y=last"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "OmkarYelsange-github-profile/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            payload = json.loads(response.read().decode("utf-8"))

        days = payload.get("contributions", [])
        total = payload.get("total", {}).get("lastYear", 0)
        if not isinstance(days, list):
            raise ValueError("Contribution API returned an unexpected response.")
        return days, int(total)
    except Exception as exc:
        print(
            f"Warning: unable to load contribution data for {user}: {exc}",
            file=sys.stderr,
        )
        return [], 0


def render(days: list[dict], total: int) -> str:
    '''Build an animated SVG heatmap with a staggered entrance and a looping glow.'''
    cell, gap, left, top = 13, 3, 34, 28
    colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

    if not days:
        return '''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="160" viewBox="0 0 860 160">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#111722"/>
    <stop offset="1" stop-color="#0d1117"/>
  </linearGradient>
</defs>
<style>
@keyframes terminalPulse { 0%,100% { opacity:.55 } 50% { opacity:1 } }
.waiting { animation:terminalPulse 1.8s ease-in-out infinite }
</style>
<rect width="860" height="160" rx="12" fill="url(#bg)"/>
<rect x="0.5" y="0.5" width="859" height="159" rx="12" fill="none" stroke="#30363d"/>
<text x="40" y="55" fill="#7d8590" font-size="15" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">omkar@github: ~/contributions</text>
<text x="40" y="92" fill="#e6edf3" font-size="22" font-weight="700" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">Waiting for contribution data</text>
<text class="waiting" x="40" y="123" fill="#7d8590" font-size="14" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">Check network access or run the contribution refresh workflow.</text>
</svg>'''

    normalized = []
    for day in days:
        try:
            parsed = dt.date.fromisoformat(str(day["date"]))
            count = int(day.get("count", 0))
            level = max(0, min(4, int(day.get("level", 0))))
        except (KeyError, TypeError, ValueError):
            continue
        normalized.append({"date": parsed, "count": count, "level": level})

    normalized.sort(key=lambda item: item["date"])
    if not normalized:
        return render([], 0)

    # Align the first date to its weekday so rows correspond to the calendar.
    first_weekday = normalized[0]["date"].weekday()  # Monday=0
    columns = (first_weekday + len(normalized) + 6) // 7
    width = left + columns * (cell + gap) + 12
    height = top + 7 * (cell + gap) + 42
    reveal_span = max(columns - 1 + 6 * 0.65, 1)

    labels = []