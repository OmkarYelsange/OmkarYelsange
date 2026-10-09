#!/usr/bin/env python3
"""Prepare a portrait photo for the ASCII renderer."""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

ROOT = Path(__file__).resolve().parents[1]
INPUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "source-photo.png"
OUTPUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "source-prepped.png"


def main():
    cutout = remove(Image.open(INPUT).convert("RGBA"))
    rgb = np.array(cutout.convert("RGB"))
    alpha = np.array(cutout.getchannel("A"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    smooth = gray
    for _ in range(3):
        smooth = cv2.bilateralFilter(smooth, 9, 40, 9)

    subject = smooth[alpha > 128]
    if len(subject) == 0:
        raise RuntimeError("No foreground detected after background removal.")

    low, high = np.percentile(subject, [2, 92])
    high = max(high, low + 1)
    tone = np.clip((smooth.astype(np.float32) - low) / (high - low), 0, 1)
    fine = cv2.GaussianBlur(smooth, (0, 0), 1.5).astype(np.float32)
    coarse = cv2.GaussianBlur(smooth, (0, 0), 6).astype(np.float32)
    ridges = np.clip((coarse - fine) / 40.0, 0, 1)
    result = np.clip(tone - 0.6 * ridges, 0, 1) * 255
    mask = cv2.GaussianBlur(alpha.astype(np.float32) / 255.0, (0, 0), 1.0)
    result = result * mask + 255.0 * (1.0 - mask)

    ys, xs = np.where(alpha > 20)
    if len(xs) == 0:
        raise RuntimeError("Foreground mask is empty.")

    side = max(xs.max() - xs.min(), ys.max() - ys.min()) + 60
    cx, cy = int((xs.min() + xs.max()) / 2), int((ys.min() + ys.max()) / 2)
    canvas = np.full((side, side), 255, dtype=np.uint8)
    x0, y0 = cx - side // 2, cy - side // 2
    sx0, sy0 = max(x0, 0), max(y0, 0)
    sx1, sy1 = min(x0 + side, result.shape[1]), min(y0 + side, result.shape[0])
    dx, dy = sx0 - x0, sy0 - y0
    canvas[dy:dy+(sy1-sy0), dx:dx+(sx1-sx0)] = result[sy0:sy1, sx0:sx1].astype(np.uint8)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(canvas, mode="L").save(OUTPUT)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
