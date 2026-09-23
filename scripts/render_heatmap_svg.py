from pathlib import Path
from datetime import date
import json
import math


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    ROOT_DIR
    / "data"
    / "contributions.json"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "assets"
    / "contrib-heatmap.svg"
)


# ============================================================
# DESIGN
# ============================================================

WIDTH = 860
HEIGHT = 205

CELL_SIZE = 11
GAP = 3

LEFT = 34
TOP = 38

ROWS = 7
COLUMNS = 53

PALETTE = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
    "#69f0a0",
]


# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Missing {INPUT_FILE}"
        )

    return json.loads(
        INPUT_FILE.read_text(
            encoding="utf-8"
        )
    )


# ============================================================
# BUILD DAY LOOKUP
# ============================================================

def build_lookup(days):
    lookup = {}

    for day in days:
        lookup[day["date"]] = day

    return lookup


# ============================================================
# CREATE SVG
# ============================================================

def create_svg(data):
    username = data.get(
        "username",
        "OmkarYelsange",
    )

    days = data.get(
        "days",
        [],
    )

    current_streak = data.get(
        "current_streak",
        0,
    )

    longest_streak = data.get(
        "longest_streak",
        0,
    )

    best_day = data.get(
        "best_day",
        {},
    )

    lookup = build_lookup(days)

    svg = []

    # --------------------------------------------------------
    # SVG HEADER
    # --------------------------------------------------------

    svg.append(
        f'''<?xml version="1.0" encoding="UTF-8"?>
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}"
    role="img"
    aria-label="GitHub contribution heatmap for {username}"
>
<title>{username} GitHub contribution heatmap</title>
'''
    )

    # --------------------------------------------------------
    # BACKGROUND
    # --------------------------------------------------------

    svg.append(
        f'''
<rect
    x="1"
    y="1"
    width="{WIDTH - 2}"
    height="{HEIGHT - 2}"
    rx="12"
    fill="#0d1117"
    stroke="#30363d"
/>
'''
    )

    # --------------------------------------------------------
    # TERMINAL HEADER
    # --------------------------------------------------------

    svg.append(
        '<circle cx="20" cy="20" r="5" fill="#ff5f56"/>'
    )

    svg.append(
        '<circle cx="38" cy="20" r="5" fill="#ffbd2e"/>'
    )

    svg.append(
        '<circle cx="56" cy="20" r="5" fill="#27c93f"/>'
    )

    svg.append(
        f'''
<text
    x="75"
    y="25"
    font-family="monospace"
    font-size="13"
    fill="#8b949e"
>
    {username}@github ~ $ ./contributions.sh
</text>
'''
    )

    # --------------------------------------------------------
    # CONTRIBUTION GRID
    # --------------------------------------------------------

    # Sort days chronologically.
    sorted_days = sorted(
        days,
        key=lambda item: item["date"],
    )

    # Use the most recent 53 weeks.
    if len(sorted_days) > 371:
        sorted_days = sorted_days[-371:]

    # Align to Sunday.
    if sorted_days:
        first_date = date.fromisoformat(
            sorted_days[0]["date"]
        )

        first_date = (
            first_date
            - __import__("datetime").timedelta(
                days=(first_date.weekday() + 1) % 7
            )
        )

        start_date = first_date
    else:
        start_date = date.today()

    # Draw 53 x 7 cells.
    for week in range(COLUMNS):
        for weekday in range(ROWS):

            current_date = (
                start_date
                + __import__("datetime").timedelta(
                    days=week * 7 + weekday
                )
            )

            key = current_date.isoformat()

            day_data = lookup.get(
                key,
                {},
            )

            level = int(
                day_data.get(
                    "level",
                    0,
                )
            )

            level = max(
                0,
                min(
                    level,
                    len(PALETTE) - 1,
                ),
            )

            x = (
                LEFT
                + week * (CELL_SIZE + GAP)
            )

            y = (
                TOP
                + weekday * (CELL_SIZE + GAP)
            )

            delay = (
                (week * 7 + weekday)
                * 0.012
            )

            svg.append(
                f'''
<rect
    x="{x}"
    y="{y}"
    width="{CELL_SIZE}"
    height="{CELL_SIZE}"
    rx="3"
    fill="{PALETTE[level]}"
    opacity="0"
>
    <animate
        attributeName="opacity"
        from="0"
        to="1"
        begin="{delay:.3f}s"
        dur="0.35s"
        fill="freeze"
    />
</rect>
'''
            )

    # --------------------------------------------------------
    # LEGEND
    # --------------------------------------------------------

    legend_y = 122

    svg.append(
        '''
<text
    x="34"
    y="160"
    font-family="monospace"
    font-size="11"
    fill="#8b949e"
>
    Less
</text>
'''
    )

    for index, color in enumerate(PALETTE):
        x = 65 + index * 16

        svg.append(
            f'''
<rect
    x="{x}"
    y="151"
    width="11"
    height="11"
    rx="3"
    fill="{color}"
/>
'''
        )

    svg.append(
        '''
<text
    x="170"
    y="160"
    font-family="monospace"
    font-size="11"
    fill="#8b949e"
>
    More
</text>
'''
    )

    # --------------------------------------------------------
    # STATS
    # --------------------------------------------------------

    best_text = "—"

    if best_day:
        best_text = (
            f'{best_day.get("count", 0)} '
            f'on {best_day.get("date", "—")}'
        )

    stats = (
        f"Current streak: {current_streak} days"
        f"   •   "
        f"Longest streak: {longest_streak} days"
        f"   •   "
        f"Best day: {best_text}"
    )

    svg.append(
        f'''
<text
    x="34"
    y="188"
    font-family="monospace"
    font-size="10"
    fill="#8b949e"
>
    {stats}
</text>
'''
    )

    svg.append("</svg>")

    return "".join(svg)


# ============================================================
# MAIN
# ============================================================

def main():
    data = load_data()

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    svg = create_svg(data)

    OUTPUT_FILE.write_text(
        svg,
        encoding="utf-8",
    )

    print(
        f"Created: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()