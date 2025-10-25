#!/usr/bin/env python3
"""
Step3_extract_both.py
---------------------
Extract BOTH:
  • Yellow waveform outline
  • White horizontal baseline (near 'cm/s')

Outputs:
  - yellow_line.png      : transparent PNG with yellow line only
  - white_line.png       : transparent PNG with white line only
  - combined_lines.png   : transparent PNG with both together
"""

import cv2
import numpy as np
from pathlib import Path
from PIL import Image

# === CONFIG ===
IN_PATH = Path("pic_2_crop.png")            # your image
OUT_YELLOW = Path("yellow_line.png")
OUT_WHITE = Path("white_line.png")
OUT_COMBINED = Path("combined_lines.png")

# Color thresholds (HSV)
LOWER_YELLOW = (15, 80, 80)            # yellow/gold tone
UPPER_YELLOW = (45, 255, 255)
WHITE_THRESH = 180                     # brightness threshold
# ==============

# 1️⃣ Load image
bgr = cv2.imread(str(IN_PATH), cv2.IMREAD_COLOR)
if bgr is None:
    raise FileNotFoundError(f"Could not read {IN_PATH}")
h, w = bgr.shape[:2]

# Convert color spaces
hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

# 2️⃣ Detect yellow waveform
mask_yellow = cv2.inRange(hsv, np.array(LOWER_YELLOW), np.array(UPPER_YELLOW))
mask_yellow = cv2.morphologyEx(mask_yellow, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8), iterations=1)

# 3️⃣ Detect white baseline
_, mask_white = cv2.threshold(gray, WHITE_THRESH, 255, cv2.THRESH_BINARY)
horizontal = cv2.morphologyEx(mask_white, cv2.MORPH_OPEN,
                              cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1)))
mask_white = cv2.bitwise_and(mask_white, horizontal)

# Keep the longest horizontal contour (the baseline)
contours, _ = cv2.findContours(mask_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
if contours:
    biggest = max(contours, key=cv2.contourArea)
    mask_white = np.zeros_like(mask_white)
    cv2.drawContours(mask_white, [biggest], -1, 255, thickness=cv2.FILLED)

# 4️⃣ Convert to RGBA layers
rgba_yellow = np.zeros((h, w, 4), dtype=np.uint8)
rgba_white = np.zeros((h, w, 4), dtype=np.uint8)

# Yellow: keep color where mask is set
idx_y = mask_yellow > 0
rgba_yellow[idx_y, :3] = bgr[idx_y][:, ::-1]  # BGR→RGB
rgba_yellow[idx_y, 3] = 255

# White line: pure white, opaque where mask is set
rgba_white[idx_y, :] = [255, 255, 255, 0]     # start clean
idx_w = mask_white > 0
rgba_white[idx_w, :3] = [255, 255, 255]
rgba_white[idx_w, 3] = 255

# 5️⃣ Combine both
combined = np.zeros_like(rgba_white)
combined[..., :3] = np.clip(
    rgba_yellow[..., :3].astype(np.uint16) + rgba_white[..., :3].astype(np.uint16), 0, 255
).astype(np.uint8)
combined[..., 3] = np.maximum(rgba_yellow[..., 3], rgba_white[..., 3])

# 6️⃣ Save results
Image.fromarray(rgba_yellow, "RGBA").save(OUT_YELLOW)
Image.fromarray(rgba_white, "RGBA").save(OUT_WHITE)
Image.fromarray(combined, "RGBA").save(OUT_COMBINED)

print("✅ Extraction complete:")
print(f" - Yellow waveform: {OUT_YELLOW}")
print(f" - White baseline:  {OUT_WHITE}")
print(f" - Combined lines:  {OUT_COMBINED}")
