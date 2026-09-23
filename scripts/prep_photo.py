from pathlib import Path

import cv2
import numpy as np
from PIL import Image


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

SOURCE_IMAGE = ROOT_DIR / "PP.png"

# Temporary processed image.
# make_ascii_svg.py will use this file.
PREPARED_IMAGE = ROOT_DIR / "prepped.png"


# ============================================================
# IMAGE PREPARATION
# ============================================================

def prepare_image():
    if not SOURCE_IMAGE.exists():
        raise FileNotFoundError(
            f"Could not find source image: {SOURCE_IMAGE}"
        )

    # --------------------------------------------------------
    # Read image
    # --------------------------------------------------------

    image = cv2.imread(
        str(SOURCE_IMAGE),
        cv2.IMREAD_COLOR,
    )

    if image is None:
        raise RuntimeError(
            "OpenCV could not read PP.png"
        )

    # --------------------------------------------------------
    # Resize if extremely large
    # --------------------------------------------------------

    height, width = image.shape[:2]

    max_dimension = 1600

    if max(height, width) > max_dimension:
        scale = (
            max_dimension
            / max(height, width)
        )

        image = cv2.resize(
            image,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_AREA,
        )

    # --------------------------------------------------------
    # Convert to LAB
    # --------------------------------------------------------

    lab = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2LAB,
    )

    l_channel, a_channel, b_channel = (
        cv2.split(lab)
    )

    # --------------------------------------------------------
    # CLAHE contrast enhancement
    # --------------------------------------------------------

    clahe = cv2.createCLAHE(
        clipLimit=2.5,
        tileGridSize=(8, 8),
    )

    l_channel = clahe.apply(
        l_channel
    )

    enhanced = cv2.merge(
        [
            l_channel,
            a_channel,
            b_channel,
        ]
    )

    enhanced = cv2.cvtColor(
        enhanced,
        cv2.COLOR_LAB2BGR,
    )

    # --------------------------------------------------------
    # Grayscale
    # --------------------------------------------------------

    gray = cv2.cvtColor(
        enhanced,
        cv2.COLOR_BGR2GRAY,
    )

    # --------------------------------------------------------
    # Slight blur
    # --------------------------------------------------------

    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0,
    )

    # --------------------------------------------------------
    # Normalize contrast
    # --------------------------------------------------------

    gray = cv2.normalize(
        gray,
        None,
        0,
        255,
        cv2.NORM_MINMAX,
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    output = Image.fromarray(
        gray
    ).convert("L")

    output.save(
        PREPARED_IMAGE
    )

    print(
        f"Prepared image created: {PREPARED_IMAGE}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    prepare_image()