# --- STEP 1: load DICOM in COLOR (keep RGB) and pick ROI interactively ---
import pydicom, numpy as np, matplotlib.pyplot as plt, cv2
from matplotlib.widgets import RectangleSelector

def load_dicom_rgb(path):
    """Load a DICOM and return an RGB uint8 image (H,W,3), preserving color when present."""
    ds = pydicom.dcmread(path)

    # Try VOI LUT if present for better windowing of grayscale
    try:
        from pydicom.pixel_data_handlers.util import apply_voi_lut
        arr = apply_voi_lut(ds.pixel_array, ds)
    except Exception:
        arr = ds.pixel_array

    photometric = str(getattr(ds, "PhotometricInterpretation", "")).upper()
    samples_per_pixel = int(getattr(ds, "SamplesPerPixel", 1))

    # If color
    if samples_per_pixel == 3 or "RGB" in photometric:
        # ensure uint8
        if arr.dtype != np.uint8:
            arr = cv2.normalize(arr.astype(np.float32), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        if arr.ndim == 3 and arr.shape[-1] == 3:
            rgb = arr
        elif arr.ndim == 3 and arr.shape[0] == 3 and arr.ndim == 3:
            rgb = np.moveaxis(arr, 0, -1)  # planar -> interleaved
        else:
            # fallback if something unusual: force to 3-channel
            if arr.ndim == 2:
                arr = cv2.cvtColor(arr, cv2.COLOR_GRAY2RGB)
            else:
                arr = arr[..., :3] if arr.shape[-1] >= 3 else arr
                if arr.ndim == 2:
                    arr = cv2.cvtColor(arr, cv2.COLOR_GRAY2RGB)
            rgb = arr
    else:
        # Grayscale: convert to RGB for display, keep full dynamic range
        # Handle MONOCHROME1 (inverted)
        if "MONOCHROME1" in photometric:
            arr = np.max(arr) - arr
        arr = cv2.normalize(arr.astype(np.float32), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        rgb = cv2.cvtColor(arr, cv2.COLOR_GRAY2RGB)

    return rgb

# 1) load DICOM (COLOR preserved)
ds_path = "./A0005"  # your file
img_rgb = load_dicom_rgb(ds_path)
H, W, _ = img_rgb.shape
print(f"image size: {H} x {W}")

# 2) interactive ROI picker on COLOR image
roi_coords = {}   # will get populated by the callback

fig, ax = plt.subplots(figsize=(7,6))
ax.imshow(img_rgb)   # no cmap -> true color
ax.set_title("Drag a rectangle over the SPECTRAL DOPPLER panel (then run Step 2)")
ax.axis('off')

def onselect(eclick, erelease):
    x0, y0 = int(min(eclick.xdata,  erelease.xdata)), int(min(eclick.ydata,  erelease.ydata))
    x1, y1 = int(max(eclick.xdata,  erelease.xdata)), int(max(eclick.ydata,  erelease.ydata))
    roi_coords['x0'], roi_coords['y0'], roi_coords['x1'], roi_coords['y1'] = x0, y0, x1, y1
    print("ROI set:", roi_coords)

rs = RectangleSelector(ax, onselect, useblit=False, button=[1], interactive=True, minspanx=10, minspany=10)
plt.show()
