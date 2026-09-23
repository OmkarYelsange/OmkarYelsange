from pathlib import Path
from datetime import date, timedelta

import json
import os
import re

import requests
from bs4 import BeautifulSoup


# ============================================================
# CONFIGURATION
# ============================================================

USERNAME = os.getenv(
    "GITHUB_USERNAME",
    "OmkarYelsange",
)

CONTRIBUTIONS_URL = (
    f"https://github.com/users/{USERNAME}/contributions"
)

ROOT_DIR = Path(__file__).resolve().parent.parent

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "contributions.json"
)


# ============================================================
# FETCH GITHUB CONTRIBUTION PAGE
# ============================================================

def fetch_page():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/153.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,"
            "application/xhtml+xml,"
            "application/xml;q=0.9,"
            "image/avif,"
            "image/webp,"
            "*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"https://github.com/{USERNAME}",
    }

    response = requests.get(
        CONTRIBUTIONS_URL,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    return response.text


# ============================================================
# EXTRACT CONTRIBUTION COUNT FROM TOOLTIP
# ============================================================

def extract_count_from_tooltip(
    soup,
    cell_id,
):
    """
    GitHub stores the exact contribution count in a
    <tool-tip> element associated with the contribution
    cell's id.
    """

    if not cell_id:
        return 0

    tooltip = soup.find(
        "tool-tip",
        attrs={
            "for": cell_id
        },
    )

    if tooltip:
        tooltip_text = tooltip.get_text(
            " ",
            strip=True,
        )

        match = re.search(
            r"([\d,]+)\s+contributions?",
            tooltip_text,
            re.IGNORECASE,
        )

        if match:
            return int(
                match.group(1).replace(",", "")
            )

    return 0


# ============================================================
# FALLBACK COUNT EXTRACTION
# ============================================================

def extract_count_from_cell(cell):
    """
    Fallback for GitHub markup variations.

    Some versions of the contribution calendar expose
    the count through title/aria-label attributes.
    """

    attributes_to_check = [
        "aria-label",
        "title",
    ]

    for attribute in attributes_to_check:

        value = cell.get(
            attribute,
            "",
        )

        if not value:
            continue

        match = re.search(
            r"([\d,]+)\s+contributions?",
            value,
            re.IGNORECASE,
        )

        if match:
            return int(
                match.group(1).replace(",", "")
            )

    return 0


# ============================================================
# PARSE CONTRIBUTION CELLS
# ============================================================

def parse_contributions(html_content):

    soup = BeautifulSoup(
        html_content,
        "html.parser",
    )

    days = []

    # --------------------------------------------------------
    # Find contribution calendar cells
    # --------------------------------------------------------

    cells = soup.select(
        "td.ContributionCalendar-day[data-date]"
    )

    # Fallback selector
    if not cells:
        cells = soup.select(
            "td[data-date][data-level]"
        )

    if not cells:
        raise RuntimeError(
            "GitHub contribution cells were not found. "
            "GitHub may have changed its page structure."
        )

    # --------------------------------------------------------
    # Parse each day
    # --------------------------------------------------------

    for cell in cells:

        date_value = cell.get(
            "data-date"
        )

        level_value = cell.get(
            "data-level",
            "0",
        )

        if not date_value:
            continue

        # ----------------------------------------------------
        # Parse contribution level
        # ----------------------------------------------------

        try:
            level = int(
                level_value
            )
        except (
            ValueError,
            TypeError,
        ):
            level = 0

        # ----------------------------------------------------
        # Parse exact contribution count
        # ----------------------------------------------------

        cell_id = cell.get(
            "id"
        )

        count = extract_count_from_tooltip(
            soup,
            cell_id,
        )

        # Fallback if tooltip wasn't found
        if count == 0:
            count = extract_count_from_cell(
                cell
            )

        # ----------------------------------------------------
        # Store day
        # ----------------------------------------------------

        days.append(
            {
                "date": date_value,
                "count": count,
                "level": level,
            }
        )

    # --------------------------------------------------------
    # Remove duplicate dates
    # --------------------------------------------------------

    unique_days = {}

    for day in days:
        unique_days[
            day["date"]
        ] = day

    days = list(
        unique_days.values()
    )

    # --------------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------------

    days.sort(
        key=lambda item: item["date"]
    )

    return days


# ============================================================
# STREAK CALCULATIONS
# ============================================================

def calculate_streaks(days):

    if not days:
        return 0, 0

    # --------------------------------------------------------
    # Get all dates with at least one contribution
    # --------------------------------------------------------

    contribution_dates = {
        date.fromisoformat(day["date"])
        for day in days
        if day["count"] > 0
    }

    if not contribution_dates:
        return 0, 0

    # --------------------------------------------------------
    # Calculate longest streak
    # --------------------------------------------------------

    parsed_dates = sorted(
        contribution_dates
    )

    longest = 1
    current = 1

    for index in range(
        1,
        len(parsed_dates),
    ):

        difference = (
            parsed_dates[index]
            - parsed_dates[index - 1]
        ).days

        if difference == 1:

            current += 1

            longest = max(
                longest,
                current,
            )

        else:
            current = 1

    # --------------------------------------------------------
    # Calculate current streak
    #
    # IMPORTANT:
    # Use the latest date actually returned by GitHub's
    # contribution calendar instead of relying on the
    # computer's local date.
    # --------------------------------------------------------

    latest_calendar_date = max(
        date.fromisoformat(day["date"])
        for day in days
    )

    # If the latest calendar date has no contribution,
    # there is no active streak ending on that date.
    if latest_calendar_date not in contribution_dates:
        return 0, longest

    current_streak = 0
    streak_date = latest_calendar_date

    while streak_date in contribution_dates:

        current_streak += 1

        streak_date -= timedelta(
            days=1
        )

    return (
        current_streak,
        longest,
    )


# ============================================================
# BEST DAY
# ============================================================

def calculate_best_day(days):

    if not days:
        return {}

    best = max(
        days,
        key=lambda item: item["count"],
    )

    if best["count"] <= 0:
        return {}

    return {
        "date": best["date"],
        "count": best["count"],
    }


# ============================================================
# MONTHLY TOTALS
# ============================================================

def calculate_monthly_totals(days):

    totals = {}

    for day in days:

        month = day[
            "date"
        ][:7]

        totals.setdefault(
            month,
            0,
        )

        totals[month] += day[
            "count"
        ]

    return totals


# ============================================================
# TOTAL CONTRIBUTIONS
# ============================================================

def calculate_total(days):

    return sum(
        day["count"]
        for day in days
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        f"Fetching contributions for "
        f"{USERNAME}..."
    )

    print(
        f"Source: {CONTRIBUTIONS_URL}"
    )

    # --------------------------------------------------------
    # Fetch HTML
    # --------------------------------------------------------

    html_content = fetch_page()

    print(
        f"Downloaded {len(html_content):,} "
        f"characters from GitHub."
    )

    # --------------------------------------------------------
    # Parse days
    # --------------------------------------------------------

    days = parse_contributions(
        html_content
    )

    if not days:
        raise RuntimeError(
            "No contribution days were found."
        )

    # --------------------------------------------------------
    # Calculate statistics
    # --------------------------------------------------------

    current_streak, longest_streak = (
        calculate_streaks(days)
    )

    best_day = calculate_best_day(
        days
    )

    monthly_totals = (
        calculate_monthly_totals(
            days
        )
    )

    total_contributions = (
        calculate_total(days)
    )

    active_days = sum(
        1
        for day in days
        if day["count"] > 0
    )

    # --------------------------------------------------------
    # Build output
    # --------------------------------------------------------

    result = {
        "username": USERNAME,

        "total_contributions": (
            total_contributions
        ),

        "active_days": active_days,

        "days": days,

        "current_streak": (
            current_streak
        ),

        "longest_streak": (
            longest_streak
        ),

        "best_day": best_day,

        "monthly_totals": (
            monthly_totals
        ),
    }

    # --------------------------------------------------------
    # Save JSON
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            result,
            indent=2,
        ),
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # Print summary
    # --------------------------------------------------------

    print()
    print("=" * 55)
    print("GitHub Contribution Summary")
    print("=" * 55)

    print(
        f"Username          : {USERNAME}"
    )

    print(
        f"Contribution days  : {len(days)}"
    )

    print(
        f"Active days        : {active_days}"
    )

    print(
        f"Total contributions: {total_contributions}"
    )

    print(
        f"Current streak     : {current_streak}"
    )

    print(
        f"Longest streak     : {longest_streak}"
    )

    print(
        f"Best day           : {best_day}"
    )

    print(
        f"Created            : {OUTPUT_FILE}"
    )

    print("=" * 55)


if __name__ == "__main__":
    main()