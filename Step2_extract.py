#!/usr/bin/env python3
"""
Step2_extract.py
----------------
Open 'pic_1.jpg', crop a fixed ROI, and save the cropped section as 'pic_1_crop.png'.
"""

from pathlib import Path
from PIL import Image, ImageOps

def main():
    # === CONFIGURATION ===
    in_path = Path("pic_1.jpg")      # input image filename
    out_path = Path("pic_1_crop.png") # output file
    ROI = {'x0': 105, 'y0': 656, 'x1': 1187, 'y1': 894}  # <— adjust here when needed
    # ======================

    if not in_path.exists():
        raise FileNotFoundError(f"Input image not found: {in_path}")

    # Open and auto-rotate according to EXIF
    img = Image.open(in_path)
    img = ImageOps.exif_transpose(img)

    # Clamp ROI to image bounds
    w, h = img.size
    x0 = max(0, min(ROI['x0'], w))
    x1 = max(0, min(ROI['x1'], w))
    y0 = max(0, min(ROI['y0'], h))
    y1 = max(0, min(ROI['y1'], h))
    if x1 <= x0 or y1 <= y0:
        raise ValueError(f"Invalid ROI after clamping: {ROI}")

    # Crop and save
    cropped = img.crop((x0, y0, x1, y1))
    cropped.save(out_path, format="PNG")

    print(f"✅ Cropped region saved as {out_path}")
    print(f"ROI used: ({x0}, {y0}) → ({x1}, {y1})")
    print(f"Output size: {cropped.size[0]}x{cropped.size[1]}")

if __name__ == "__main__":
    main()
