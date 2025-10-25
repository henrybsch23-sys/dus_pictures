# 3. Preprocess (crop margins -> normalize -> make a clean "analysis image")

import numpy as np, cv2, matplotlib.pyplot as plt
import pydicom
from matplotlib.widgets import RectangleSelector

ds = pydicom.dcmread("./A0023")
img = ds.pixel_array
if img.ndim == 3:
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)
H, W = img.shape
print(f"image size: {H} x {W}")

roi_coords= {'x0': 107, 'y0': 704, 'x1': 1188, 'y1': 891}

y0, y1, x0, x1 = roi_coords['y0'], roi_coords['y1'], roi_coords['x0'], roi_coords['x1']

spec = img[y0:y1, x0:x1]

px_per_s = 179.92 
px_per_cms = 2.435
v0_row = 145

cal = {"px_per_s": float(px_per_s), "px_per_cms": float(px_per_cms), "v0_row": int(v0_row)}

# --- 3.1 (optional) trim tiny margins to remove axis ticks/text inside the ROI ---
# tweak these if you still see labels in the preview
pad_top, pad_bottom, pad_left, pad_right = 4, 4, 4, 4
roi = spec[pad_top: spec.shape[0]-pad_bottom,
           pad_left: spec.shape[1]-pad_right]

# --- 3.2 convert to float32 and robust-normalize to [0,1] (P2–P98) ---
im = roi.astype(np.float32)
p2, p98 = np.percentile(im, [2, 98])
im = np.clip((im - p2) / (p98 - p2 + 1e-6), 0, 1)

# (optional) local contrast boost (CLAHE) if the strip looks very flat)
use_clahe = False
if use_clahe:
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    im = clahe.apply((im*255).astype(np.uint8)).astype(np.float32)/255.0

# --- 3.3 build an analysis mask to ignore non-informative regions ---
H, W = im.shape
mask = np.ones_like(im, dtype=np.uint8)

# Exclude top/bottom 1% (possible borders)
b = max(1, int(0.01*H))
mask[:b,:] = 0; mask[-b:,:] = 0

# Exclude a wall-filter band around 0 cm/s (±5 cm/s) which is often dark
band = int(5.0 * cal["px_per_cms"])
r0 = np.clip(cal["v0_row"] - pad_top, 0, H-1)  # adjust for the pad we removed
mask[max(0, r0-band): min(H, r0+band), :] = 0

# Optional: exclude left/right 1% (axes/labels)
b2 = max(1, int(0.01*W))
mask[:, :b2] = 0; mask[:, -b2:] = 0

# --- 3.4 final image used for thresholding/tracing ---
im_for_thresh = im.copy()
im_for_thresh[mask==0] = 0.0

# --- 3.5 sanity check preview ---
fig, axs = plt.subplots(1,3, figsize=(12,4))
axs[0].imshow(roi, cmap='gray'); axs[0].set_title("ROI (trimmed)"); axs[0].axis('off')
axs[1].imshow(im, cmap='gray'); axs[1].set_title("Normalized [0,1]"); axs[1].axis('off')
axs[2].imshow(im_for_thresh, cmap='gray'); axs[2].set_title("Masked for analysis"); axs[2].axis('off')
plt.show()
