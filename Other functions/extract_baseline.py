#!/usr/bin/env python3
"""
Step3_extract_baseline.py
-------------------------
Detect and extract the flat horizontal white baseline (near 'cm/s') 
from the given ultrasound-like velocity image.

Input:  pic.png
Output: baseline_mask.png  (binary mask of the line)
         baseline_rgba.png (transparent PNG with the line)
"""

import cv2
import numpy as np
from pathlib import Path
from PIL import Image

# === CONFIG ===
IN_PATH  = Path("pic_1.jpg")          # <- your input file
MASK_OUT = Path("baseline_mask.png")  # binary line mask
RGBA_OUT = Path("baseline_rgba.png")  # transparent line overlay
WHITE_THRESH = 180                    # brightness threshold (0–255)
MAX_LINE_THICKNESS = 4                # keep lines this many px thick
# ==============

# Load and convert to grayscale
img = cv2.imread(str(IN_PATH), cv2.IMREAD_COLOR)
if img is None:
    raise FileNotFoundError(IN_PATH)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Threshold for bright (white) pixels
_, mask = cv2.threshold(gray, WHITE_THRESH, 255, cv2.THRESH_BINARY)

# Optionally remove noise: keep only longest horizontal structures
edges = cv2.Sobel(mask, cv2.CV_8U, dx=0, dy=1, ksize=3)
horizontal = cv2.morphologyEx(mask, cv2.MORPH_OPEN,
                              cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1)))
# Keep only strong horizontal lines (connected, wide regions)
mask = cv2.bitwise_and(mask, horizontal)

# Find largest horizontal white line
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
if not contours:
    raise RuntimeError("No white line found.")
line_contour = max(contours, key=cv2.contourArea)
x, y, w, h = cv2.boundingRect(line_contour)
if h > MAX_LINE_THICKNESS:
    h = MAX_LINE_THICKNESS

# Crop narrow band around the line (± some pixels)
pad = 1
y0, y1 = max(0, y - pad), min(mask.shape[0], y + h + pad)
baseline_mask = np.zeros_like(mask)
cv2.drawContours(baseline_mask, [line_contour], -1, 255, thickness=cv2.FILLED)
baseline_mask[:y0, :] = 0
baseline_mask[y1:, :] = 0

# Save binary mask
cv2.imwrite(str(MASK_OUT), baseline_mask)

# Build transparent RGBA image showing only the white line
rgba = np.zeros((mask.shape[0], mask.shape[1], 4), dtype=np.uint8)
rgba[..., :3] = 255  # white
rgba[..., 3] = baseline_mask  # alpha = mask
Image.fromarray(rgba, mode="RGBA").save(RGBA_OUT)

print(f"✅ Baseline extracted:")
print(f" - Mask saved: {MASK_OUT}")
print(f" - RGBA saved: {RGBA_OUT}")
print(f"Line y-range: {y0}–{y1}")
