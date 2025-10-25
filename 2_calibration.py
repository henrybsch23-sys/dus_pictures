import numpy as np, matplotlib.pyplot as plt
import pydicom, numpy as np, matplotlib.pyplot as plt, cv2
from matplotlib.widgets import RectangleSelector

# 2) load DICOM and convert to grayscale
ds = pydicom.dcmread("./A0005")
img = ds.pixel_array
if img.ndim == 3:
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)
H, W = img.shape
print(f"image size: {H} x {W}")

roi_coords= {'x0': 107, 'y0': 655, 'x1': 1187, 'y1': 895}

y0, y1, x0, x1 = roi_coords['y0'], roi_coords['y1'], roi_coords['x0'], roi_coords['x1']

spec = img[y0:y1, x0:x1]

# 1) TIME: click two vertical gridlines
plt.figure(figsize=(6,4)); plt.imshow(spec, cmap='gray'); plt.title("Click TWO vertical time gridlines"); plt.axis('off')
tpts = plt.ginput(2, timeout=0); plt.close()

x0_t, y0_t = tpts[0]  # (x,y)
x1_t, y1_t = tpts[1]
px_span_seconds = abs(x1_t - x0_t)

# >>> EDIT THIS to what those two gridlines represent in seconds (read from screen label)
seconds_span = 6.0    # e.g., 2.0 if they’re two seconds apart

px_per_s = px_span_seconds / seconds_span
fs_env = px_per_s  # envelope samples per second along x-axis

print(f"Time calibration: {px_span_seconds:.1f} px == {seconds_span} s  →  {px_per_s:.2f} px/s")

# 2) VELOCITY: click 0 cm/s line, then a +V tick (e.g., +100 cm/s)
plt.figure(figsize=(6,4)); plt.imshow(spec, cmap='gray'); plt.title("Click ZERO-velocity line, then a +V tick (e.g., +100 cm/s)"); plt.axis('off')
vpts = plt.ginput(2, timeout=0); plt.close()

x0_v, y0_v = vpts[0]  # (x,y) for 0 cm/s
x1_v, y1_v = vpts[1]  # (x,y) for +V tick
v0_row = int(round(y0_v))
px_span_vel = abs(y1_v - y0_v)

# >>> EDIT THIS to the value of that tick in cm/s (e.g., 100.0)
vel_span = 53.4

px_per_cms = px_span_vel / vel_span
print(f"Velocity calibration: {px_span_vel:.1f} px == {vel_span} cm/s  →  {px_per_cms:.3f} px/(cm/s)")

# Pack in a dict for later steps
cal = {
    "px_per_s": float(px_per_s),
    "px_per_cms": float(px_per_cms),
    "v0_row": int(v0_row)  # row index within ROI that corresponds to 0 cm/s
}
cal
