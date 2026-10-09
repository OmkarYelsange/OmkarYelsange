#!/usr/bin/env python3
"""Convert a preprocessed portrait into a typing monochrome ASCII SVG."""

from __future__ import annotations

import html
import os
import sys
from pathlib import Path
from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "source-prepped.png"
OUTPUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "omkar-ascii.svg"
COLS = int(os.environ.get("COLS", "180"))
ART_W = 800
CELL_W = ART_W / COLS
CELL_H = CELL_W * 15 / 8
ROWS = round(COLS * 8 / 15)
RAMP = " .`:-=+*cs#%@"
PAD, TITLE_H, STATUS_H = 20, 30, 30
ART_H = ROWS * CELL_H
CANVAS_W = ART_W + 2 * PAD
CANVAS_H = TITLE_H + ART_H + STATUS_H + PAD


def placeholder():
    lines = [
        " __  __  ____  _  ________    ____  _",
        "|  \\/  |/ __ \\| |/ /  ____|  / __ \\| |",
        "| \\  / | |  | | ' /| |__    | |  | | |",
        "| |\\/| | |  | |  < |  __|   | |  | | |",
        "| |  | | |__| | . \\| |____  | |__| | |",
        "|_|  |_|\\____/|_|\\_\\______|  \\____/|_|",
    ]
    body = "".join(f'<text x="{PAD}" y="{105+i*36}" fill="#c9d1d9" font-size="30">{html.escape(line)}</text>' for i, line in enumerate(lines))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" viewBox="0 0 {CANVAS_W} {CANVAS_H}"><defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs><rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/><rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" fill="none" stroke="#30363d"/><line x1="0" y1="30" x2="{CANVAS_W}" y2="30" stroke="#30363d"/><text x="{CANVAS_W/2}" y="20" text-anchor="middle" fill="#7d8590" font-size="12" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">omkar@github: ~$ ./portrait.sh</text><g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">{body}</g><line x1="0" y1="{CANVAS_H-55}" x2="{CANVAS_W}" y2="{CANVAS_H-55}" stroke="#30363d"/><text x="{PAD}" y="{CANVAS_H-30}" fill="#7d8590" font-size="13" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">Replace source-photo.png and regenerate for your portrait.</text></svg>'''


def render(image):
    gray = ImageEnhance.Contrast(image.convert("L")).enhance(1.05).resize((COLS, ROWS), Image.Resampling.LANCZOS)
    px = gray.load()
    rows = []
    for y in range(ROWS):
        line = []
        for x in range(COLS):
            lum = (px[x, y] / 255.0) ** 1.18
            if lum >= 0.80:
                line.append(" ")
            else:
                idx = max(0, min(len(RAMP)-1, int((1.0-lum)*(len(RAMP)-1)+0.5)))
                line.append(RAMP[idx])
        rows.append("".join(line))

    row_dur = 5.8 / max(ROWS, 1)
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"><defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs><rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/><rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" fill="none" stroke="#30363d"/><line x1="0" y1="{TITLE_H}" x2="{CANVAS_W}" y2="{TITLE_H}" stroke="#30363d"/><text x="{CANVAS_W/2}" y="20" text-anchor="middle" fill="#7d8590" font-size="12">omkar@github: ~$ ./portrait.sh</text>''']
    art_top = TITLE_H + PAD * 0.35
    fs = CELL_H * 0.86
    for r, line in enumerate(rows):
        y = art_top + r * CELL_H + CELL_H * 0.74
        row_y = art_top + r * CELL_H
        delay = r * row_dur
        parts.append(f'<clipPath id="r{r}"><rect x="{PAD}" y="{row_y:.1f}" height="{CELL_H}" width="0"><animate attributeName="width" from="0" to="{ART_W}" begin="{delay:.3f}s" dur="{row_dur:.2f}s" fill="freeze"/></rect></clipPath>')
        parts.append(f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="#c9d1d9" font-size="{fs:.1f}" textLength="{ART_W}" lengthAdjust="spacing" clip-path="url(#r{r})">{html.escape(line)}</text>')
    status = TITLE_H + ART_H + PAD * 0.35
    parts.append(f'<line x1="0" y1="{status:.1f}" x2="{CANVAS_W}" y2="{status:.1f}" stroke="#30363d"/><text x="{PAD}" y="{status+19:.1f}" fill="#7d8590" font-size="13">omkar@github:~$ whoami <tspan fill="#c9d1d9">Omkar Yelsange</tspan></text></svg>')
    return "".join(parts)


def main():
    OUTPUT.write_text(placeholder() if not SOURCE.exists() else render(Image.open(SOURCE)), encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
