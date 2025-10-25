from pathlib import Path
import numpy as np
import cv2
import pandas as pd

# --- CONFIG ---
IMG_PATH = Path("combined_lines.png")  # white baseline + white waveform on transparent bg
DURATION_SEC = 9.0                     # total time span (seconds)
V_PEAK = 41.5                          # tallest peak (cm/s)
BASELINE_BAND = 3                      # pixels to remove above/below baseline
PERCENTILE_FOR_PEAK = 99.0             # robust peak percentile
# -------------

# 1) Load image (prefer RGBA so we can use alpha)
rgba = cv2.imread(str(IMG_PATH), cv2.IMREAD_UNCHANGED)
if rgba is None:
    raise FileNotFoundError(IMG_PATH)

h, w = rgba.shape[:2]

if rgba.shape[2] == 4:
    bgr = rgba[..., :3]
    alpha = rgba[..., 3]
    # Binary mask of where the lines exist (wave + baseline)
    mask_all = (alpha > 0).astype(np.uint8) * 255
else:
    bgr = rgba
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    # Fallback: threshold bright pixels (may need tuning if no alpha)
    mask_all = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)[1]

# 2) Detect baseline row as the row with the most "on" pixels
row_counts = mask_all.sum(axis=1)  # count per row (0..255 sums)
y_base = int(np.argmax(row_counts))

# 3) Build waveform mask (remove a horizontal band around the baseline)
mask_wave = mask_all.copy()
y0 = max(0, y_base - BASELINE_BAND)
y1 = min(h, y_base + BASELINE_BAND + 1)
mask_wave[y0:y1, :] = 0  # remove baseline & its halo

# Optional cleanup: tiny gaps fill, small specks remove
mask_wave = cv2.morphologyEx(mask_wave, cv2.MORPH_CLOSE, np.ones((3,3), np.uint8), iterations=1)

# 4) For each column, find the first line pixel when scanning upward from the baseline
y_vals = np.full(w, np.nan, dtype=float)  # y index of waveform for each x
for x in range(w):
    col = mask_wave[:y_base, x]  # only above baseline
    # Scan downward (from y_base-1 up)
    ys = np.where(col > 0)[0]
    if ys.size:
        # pick the one closest to baseline: the largest y index
        y_vals[x] = ys.max()

# Pixel displacement above baseline (positive upward)
pix_disp = np.where(np.isfinite(y_vals), y_base - y_vals, np.nan)

# Sanity check: if still too flat, increase BASELINE_BAND or refine mask
valid = np.isfinite(pix_disp)
if not valid.any():
    raise RuntimeError("No waveform detected; adjust thresholds.")

# ▶ Re-zero the baseline using a small percentile (robust against outliers)
BASELINE_PERCENTILE = 1.0  # try 0.5–2.0 depending on your images
baseline_offset_pix = np.nanpercentile(pix_disp[valid], BASELINE_PERCENTILE)
# Remove baseline bias and clamp negatives
pix_disp = np.maximum(0.0, pix_disp - baseline_offset_pix)

# Continue as before with scaling
peak_pix = np.nanpercentile(pix_disp[valid], 99.0) or np.nanmax(pix_disp[valid])
px_per_cms = peak_pix / V_PEAK
velocity = pix_disp / (px_per_cms if px_per_cms != 0 else 1.0)

# Interpolate NaNs linearly, clamp negatives to 0
v = velocity.copy()
idx = np.where(np.isfinite(v))[0]
if idx.size >= 2:
    v_interp = v.copy()
    v_interp[:idx[0]] = v[idx[0]]
    v_interp[idx[-1] + 1:] = v[idx[-1]]
    for a, b in zip(idx[:-1], idx[1:]):
        if b - a > 1:
            m = (v[b] - v[a]) / (b - a)
            v_interp[a+1:b] = v[a] + m * (np.arange(a+1, b) - a)
    velocity = v_interp
velocity = np.where(velocity < 0, 0.0, velocity)

# 6) Time axis and CSV
time_s = (np.arange(w) / max(1, (w - 1))) * DURATION_SEC
df = pd.DataFrame({
    "x_px": np.arange(w, dtype=int),
    "y_px": y_vals,                 # y-index of the waveform
    "time_s": time_s,               # seconds
    "velocity_cm_s": velocity       # cm/s above baseline
})
out_csv = IMG_PATH.with_suffix(".csv")
df.to_csv(out_csv, index=False)
print(f"✅ Saved: {out_csv}  (rows={len(df)})")
print(f"Baseline row: {y_base}, px_per_cms: {px_per_cms:.4f}, peak_pix: {peak_pix:.2f}")
