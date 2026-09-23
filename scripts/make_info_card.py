from pathlib import Path
import html


# ============================================================
# OMKAR YELSANGE - PROFILE CONFIGURATION
# ============================================================

NAME = "Omkar Yelsange"
USERNAME = "OmkarYelsange"

ROLE = "Data Analyst | Data Engineer"
LOCATION = "Pune, India"

STACK = [
    "Python",
    "SQL",
    "Power BI",
    "Databricks",
    "PySpark",
    "AWS",
    "Machine Learning",
]

FOCUS = [
    "Data Analytics",
    "Data Engineering",
    "Business Intelligence",
    "AI / ML",
]

CURRENTLY_LEARNING = [
    "Advanced SQL",
    "PySpark",
    "Databricks",
    "ETL Pipelines",
    "Machine Learning",
]


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = ROOT_DIR / "assets" / "info-card.svg"


# ============================================================
# SVG HELPERS
# ============================================================

def escape(value):
    """Safely escape text for SVG/XML."""
    return html.escape(str(value))


def text_element(
    x,
    y,
    text,
    size=14,
    fill="#c9d1d9",
    weight="normal",
    family="monospace",
):
    return (
        f'<text x="{x}" y="{y}" '
        f'font-family="{family}" '
        f'font-size="{size}px" '
        f'font-weight="{weight}" '
        f'fill="{fill}">'
        f"{escape(text)}</text>"
    )


# ============================================================
# BUILD SVG
# ============================================================

def build_svg():

    # Increased height so STACK + FOCUS + footer
    # have enough vertical space.
    width = 490
    height = 525

    lines = []

    # --------------------------------------------------------
    # Background
    # --------------------------------------------------------

    lines.append(
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" '
        'rx="12" fill="#0d1117" stroke="#30363d" stroke-width="2"/>'
    )

    # --------------------------------------------------------
    # Terminal top bar
    # --------------------------------------------------------

    lines.append(
        '<rect x="1" y="1" width="488" height="36" '
        'rx="12" fill="#161b22"/>'
    )

    # Cover lower corners of top bar
    lines.append(
        '<rect x="1" y="20" width="488" height="17" fill="#161b22"/>'
    )

    # Terminal dots
    lines.append('<circle cx="20" cy="19" r="5" fill="#ff5f56"/>')
    lines.append('<circle cx="38" cy="19" r="5" fill="#ffbd2e"/>')
    lines.append('<circle cx="56" cy="19" r="5" fill="#27c93f"/>')

    lines.append(
        text_element(
            75,
            24,
            f"{USERNAME} — profile",
            size=13,
            fill="#8b949e",
        )
    )

    # --------------------------------------------------------
    # Name
    # --------------------------------------------------------

    lines.append(
        text_element(
            24,
            72,
            NAME,
            size=24,
            fill="#f0f6fc",
            weight="bold",
        )
    )

    lines.append(
        text_element(
            24,
            96,
            ROLE,
            size=14,
            fill="#58a6ff",
        )
    )

    lines.append(
        text_element(
            24,
            118,
            f"Location: {LOCATION}",
            size=13,
            fill="#8b949e",
        )
    )

    # --------------------------------------------------------
    # Separator
    # --------------------------------------------------------

    lines.append(
        '<line x1="24" y1="136" x2="466" y2="136" '
        'stroke="#30363d" stroke-width="1"/>'
    )

    # --------------------------------------------------------
    # Stack
    # --------------------------------------------------------

    lines.append(
        text_element(
            24,
            164,
            "STACK",
            size=12,
            fill="#8b949e",
            weight="bold",
        )
    )

    # Starting position for stack items
    stack_y = 190

    # Vertical spacing between stack items
    stack_spacing = 22

    for index, item in enumerate(STACK):

        delay = index * 0.10

        lines.append(
            f'''
            <g opacity="0">
                <animate
                    attributeName="opacity"
                    from="0"
                    to="1"
                    begin="{delay:.2f}s"
                    dur="0.35s"
                    fill="freeze"
                />
                {text_element(
                    30,
                    stack_y,
                    "› " + item,
                    size=14,
                    fill="#c9d1d9",
                )}
            </g>
            '''
        )

        stack_y += stack_spacing

    # --------------------------------------------------------
    # Focus
    # --------------------------------------------------------

    # Add breathing room after the STACK section.
    focus_title_y = stack_y + 8

    lines.append(
        text_element(
            24,
            focus_title_y,
            "FOCUS",
            size=12,
            fill="#8b949e",
            weight="bold",
        )
    )

    # First focus item
    focus_y = focus_title_y + 28

    # More spacing between focus items
    focus_spacing = 28

    for index, item in enumerate(FOCUS):

        delay = 0.75 + (index * 0.10)

        lines.append(
            f'''
            <g opacity="0">
                <animate
                    attributeName="opacity"
                    from="0"
                    to="1"
                    begin="{delay:.2f}s"
                    dur="0.35s"
                    fill="freeze"
                />
                {text_element(
                    30,
                    focus_y,
                    "› " + item,
                    size=14,
                    fill="#c9d1d9",
                )}
            </g>
            '''
        )

        focus_y += focus_spacing

    # --------------------------------------------------------
    # Footer
    # --------------------------------------------------------

    # Position footer dynamically below the final FOCUS item.
    footer_line_y = focus_y + 2

    lines.append(
        f'<line x1="24" y1="{footer_line_y}" '
        f'x2="466" y2="{footer_line_y}" '
        'stroke="#30363d" stroke-width="1"/>'
    )
    

    # --------------------------------------------------------
    # SVG DOCUMENT
    # --------------------------------------------------------

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{width}"
    height="{height}"
    viewBox="0 0 {width} {height}"
    role="img"
    aria-label="Omkar Yelsange profile information card"
>

    <title>Omkar Yelsange — Data Analyst and Data Engineer</title>

    {''.join(lines)}

</svg>
'''

    return svg


# ============================================================
# WRITE FILE
# ============================================================

def main():

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    svg = build_svg()

    OUTPUT_FILE.write_text(
        svg,
        encoding="utf-8",
    )

    print(
        f"Created: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()