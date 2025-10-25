# --- STEP 1: load PICTURE in COLOR (keep RGB) and pick ROI interactively ---
import numpy as np
import matplotlib.pyplot as plt
import cv2
from matplotlib.widgets import RectangleSelector
from PIL import Image, ImageOps  # for EXIF-aware loading

def load_image_rgb(path):
    """
    Load a standard image file (jpg/png/tiff, etc.) and return an RGB uint8 array (H,W,3).
    - Preserves color
    - Honors EXIF orientation (e.g., phone photos)
    """
    pil_img = Image.open(path)
    pil_img = ImageOps.exif_transpose(pil_img)  # rotate if EXIF says so
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")
    rgb = np.array(pil_img, dtype=np.uint8)     # (H,W,3) RGB
    return rgb

# 1) load IMAGE (COLOR preserved)
img_path = "pic_1.jpg"  # <— your picture file
img_rgb = load_image_rgb(img_path)
H, W, _ = img_rgb.shape
print(f"image size: {H} x {W}")

# 2) interactive ROI picker on COLOR image
roi_coords = {}   # will get populated by the callback

fig, ax = plt.subplots(figsize=(7,6))
ax.imshow(img_rgb)   # true color
ax.set_title("Drag a rectangle over the SPECTRAL DOPPLER panel (then run Step 2)")
ax.axis('off')

def onselect(eclick, erelease):
    x0, y0 = int(min(eclick.xdata,  erelease.xdata)), int(min(eclick.ydata,  erelease.ydata))
    x1, y1 = int(max(eclick.xdata,  erelease.xdata)), int(max(eclick.ydata,  erelease.ydata))
    roi_coords['x0'], roi_coords['y0'], roi_coords['x1'], roi_coords['y1'] = x0, y0, x1, y1
    print("ROI set:", roi_coords)

rs = RectangleSelector(
    ax, onselect,
    useblit=False, button=[1], interactive=True,
    minspanx=10, minspany=10
)
plt.show()
