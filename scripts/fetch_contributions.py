#!/usr/bin/env python3
"""Fetch public GitHub contribution data into data/contributions.json."""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "contributions.json"
USERNAME = os.environ.get("GH_PROFILE_USER", "OmkarYelsange")


def level_for(count: int) -> int:
    if count <= 0:
        return 0
    if count <= 3:
        return 1
    if count <= 8:
        return 2
    if count <= 15:
        return 3
    return 4


def fetch_days() -> list[dict]:
    url = f"https://github.com/users/{USERNAME}/contributions"
    response = requests.get(
        url,
        headers={"User-Agent": "OmkarYelsange-github-profile/1.0"},
        timeout=30,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        raise RuntimeError("GitHub contribution cells were not found.")

    days = []
    for cell in cells:
        date_text = cell.get("data-date")
        if not date_text:
            continue

        tooltip_id = cell.get("id")
        tooltip = soup.find("tool-tip", attrs={"for": tooltip_id}) if tooltip_id else None
        message = tooltip.get_text(" ", strip=True) if tooltip else ""

        if re.search(r"no contributions", message, re.I):
            count = 0
        else:
            match = re.search(r"(\d[\d,]*)", message)
            count = int(match.group(1).replace(",", "")) if match else 0

        days.append({"date": date_text, "count": count, "level": level_for(count)})

    days.sort(key=lambda item: item["date"])
    if not days:
        raise RuntimeError("No contribution days were parsed.")
    return days


def current_streak(days: list[dict]) -> tuple[int, str | None, str | None]:
    index = len(days) - 1
    if index >= 0 and days[index]["count"] == 0:
        index -= 1

    length = 0
    end_index = index
    while index >= 0 and days[index]["count"] > 0:
        length += 1
        index -= 1

    if length == 0:
        return 0, None, None
    return length, days[index + 1]["date"], days[end_index]["date"]


def longest_streak(days: list[dict]) -> tuple[int, str | None, str | None]:
    best = run = 0
    best_start = best_end = None
    run_start = None

    for i, day in enumerate(days):
        if day["count"] > 0:
            if run == 0:
                run_start = i
            run += 1
            if run > best:
                best = run
                best_start = days[run_start]["date"]
                best_end = day["date"]
        else:
            run = 0
            run_start = None

    return best, best_start, best_end


def build_snapshot(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)
    active = sum(1 for d in days if d["count"] > 0)
    best_day = max(days, key=lambda d: d["count"])
    cur_len, cur_start, cur_end = current_streak(days)
    long_len, long_start, long_end = longest_streak(days)

    monthly = {}
    for day in days:
        key = day["date"][:7]
        monthly[key] = monthly.get(key, 0) + day["count"]

    return {
        "username": USERNAME,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": total,
        "active_days": active,
        "avg_per_active_day": round(total / active, 1) if active else 0,
        "current_streak": {"length": cur_len, "start": cur_start, "end": cur_end},
        "longest_streak": {"length": long_len, "start": long_start, "end": long_end},
        "best_day": {"date": best_day["date"], "count": best_day["count"]},
        "monthly": [{"month": m, "total": v} for m, v in sorted(monthly.items())],
        "days": days,
    }


def main() -> None:
    data = build_snapshot(fetch_days())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"wrote {OUT}: {data['total_contributions']:,} contributions")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
