import pydicom, numpy as np, matplotlib.pyplot as plt, cv2
from matplotlib.widgets import RectangleSelector

# 2) load DICOM and convert to grayscale
ds = pydicom.dcmread("./A0005")
img = ds.pixel_array
if img.ndim == 3:
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)
H, W = img.shape
print(f"image size: {H} x {W}")

# 3) interactive ROI picker
roi_coords = {}   # will get populated by the callback

fig, ax = plt.subplots(figsize=(7,6))
ax.imshow(img, cmap='gray')
ax.set_title("Drag a rectangle over the SPECTRAL DOPPLER panel (then run the next cell)")
ax.axis('off')

def onselect(eclick, erelease):
    # Ensure top-left / bottom-right ordering
    x0, y0 = int(min(eclick.xdata,  erelease.xdata)), int(min(eclick.ydata,  erelease.ydata))
    x1, y1 = int(max(eclick.xdata,  erelease.xdata)), int(max(eclick.ydata,  erelease.ydata))
    roi_coords['x0'], roi_coords['y0'], roi_coords['x1'], roi_coords['y1'] = x0, y0, x1, y1
    print("ROI set:", roi_coords)

rs = RectangleSelector(ax, onselect,
                       useblit=False, button=[1],  # left-click drag
                       interactive=True, minspanx=10, minspany=10)
plt.show()