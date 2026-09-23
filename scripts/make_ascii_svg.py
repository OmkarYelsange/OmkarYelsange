from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

INPUT_IMAGE = ROOT_DIR / "prepped.png"

OUTPUT_FILE = (
    ROOT_DIR
    / "assets"
    / "omkar-ascii.svg"
)


# ============================================================
# ASCII CONFIGURATION
# ============================================================

# Bright → dark
RAMP = " .`:-=+*cs#%@"

COLUMNS = 100

FONT_SIZE = 7

# Characters are taller than they are wide.
# This correction keeps the portrait from looking stretched.
CHARACTER_ASPECT = 0.48

TEXT_COLOR = "#c9d1d9"

BACKGROUND = "#0d1117"


# ============================================================
# IMAGE → ASCII
# ============================================================

def image_to_ascii():
    if not INPUT_IMAGE.exists():
        raise FileNotFoundError(
            "prepped.png was not found. "
            "Run prep_photo.py first."
        )

    image = Image.open(
        INPUT_IMAGE
    ).convert("L")

    width, height = image.size

    rows = max(
        1,
        int(
            COLUMNS
            * height
            / width
            * CHARACTER_ASPECT
        )
    )

    image = image.resize(
        (COLUMNS, rows),
        Image.Resampling.LANCZOS,
    )

    pixels = list(
        image.getdata()
    )

    ascii_rows = []

    for row in range(rows):
        chars = []

        for col in range(COLUMNS):
            brightness = pixels[
                row * COLUMNS + col
            ]

            # White → sparse character
            # Black → dense character
            index = int(
                (255 - brightness)
                / 255
                * (len(RAMP) - 1)
            )

            index = max(
                0,
                min(
                    index,
                    len(RAMP) - 1,
                )
            )

            chars.append(
                RAMP[index]
            )

        ascii_rows.append(
            "".join(chars)
        )

    return ascii_rows


# ============================================================
# SVG GENERATION
# ============================================================

def create_svg(rows):
    width = COLUMNS * FONT_SIZE + 20

    line_height = FONT_SIZE + 1

    height = (
        len(rows)
        * line_height
        + 20
    )

    svg = []

    svg.append(
        f'''<?xml version="1.0" encoding="UTF-8"?>
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{width}"
    height="{height}"
    viewBox="0 0 {width} {height}"
    role="img"
    aria-label="Animated ASCII portrait of Omkar Yelsange"
>

<title>Omkar Yelsange ASCII portrait</title>

<rect
    x="0"
    y="0"
    width="{width}"
    height="{height}"
    rx="10"
    fill="{BACKGROUND}"
/>

<defs>
'''
    )

    # --------------------------------------------------------
    # Clip paths
    # --------------------------------------------------------

    for index, _ in enumerate(rows):
        y = 10 + index * line_height

        svg.append(
            f'''
<clipPath id="clip-{index}">
    <rect
        x="0"
        y="{y - FONT_SIZE}"
        width="0"
        height="{line_height + 4}"
    >
        <animate
            attributeName="width"
            from="0"
            to="{width}"
            begin="{index * 0.06:.2f}s"
            dur="0.7s"
            fill="freeze"
        />
    </rect>
</clipPath>
'''
        )

    svg.append("</defs>")

    # --------------------------------------------------------
    # Rows
    # --------------------------------------------------------

    for index, row in enumerate(rows):

        y = (
            10
            + index * line_height
        )

        safe_row = escape(
            row
        )

        svg.append(
            f'''
<g clip-path="url(#clip-{index})">
    <text
        x="10"
        y="{y}"
        font-family="monospace"
        font-size="{FONT_SIZE}px"
        xml:space="preserve"
        fill="{TEXT_COLOR}"
    >{safe_row}</text>
</g>
'''
        )

    svg.append("</svg>")

    return "".join(svg)


# ============================================================
# MAIN
# ============================================================

def main():
    rows = image_to_ascii()

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    svg = create_svg(
        rows
    )

    OUTPUT_FILE.write_text(
        svg,
        encoding="utf-8",
    )

    print(
        f"Created: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()