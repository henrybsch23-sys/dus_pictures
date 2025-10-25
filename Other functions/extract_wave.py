from pathlib import Path
import numpy as np
from PIL import Image
import cv2

# -------- CONFIG --------
IN_PATH = Path("./pic_1_crop.png")           # <— change to your file
OUT_PNG = Path("yellow_line_only.png")
OUT_SVG = Path("yellow_line_only.svg")

# HSV thresholds for yellow/gold (OpenCV: H∈[0,179], S,V∈[0,255])
LOWER_YELLOW = (15, 80, 80)
UPPER_YELLOW = (45, 255, 255)

K = 3               # morphology kernel size
CLOSE_ITERS = 1     # gap-closing passes
OPEN_ITERS = 0
DO_SKELETON = False # set True for ~1px trace

# -------- PIPELINE --------
bgr = cv2.imread(str(IN_PATH), cv2.IMREAD_COLOR)
hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

# 1) Threshold for yellow
mask = cv2.inRange(hsv, np.array(LOWER_YELLOW, np.uint8), np.array(UPPER_YELLOW, np.uint8))

# 2) Clean mask
kernel = np.ones((K, K), np.uint8)
if CLOSE_ITERS: mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=CLOSE_ITERS)
if OPEN_ITERS:  mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=OPEN_ITERS)

# 3) Optional thinning
if DO_SKELETON:
    try:
        import cv2.ximgproc as xip
        mask = xip.thinning(mask, thinningType=xip.THINNING_GUOHALL)
    except Exception:
        # Simple fallback skeletonization
        element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
        skel = np.zeros_like(mask)
        img  = mask.copy()
        while True:
            eroded = cv2.erode(img, element)
            temp   = cv2.dilate(eroded, element)
            temp   = cv2.subtract(img, temp)
            skel   = cv2.bitwise_or(skel, temp)
            img    = eroded
            if cv2.countNonZero(img) == 0:
                break
        mask = skel

# 4) Build RGBA with transparency
h, w = mask.shape
rgba = np.zeros((h, w, 4), dtype=np.uint8)     # transparent canvas
idx = mask > 0
rgba[idx, :3] = bgr[idx][:, ::-1]              # keep original line color (BGR→RGB)
rgba[idx, 3]  = 255                            # opaque where line exists

# 5) Light antialias of alpha
rgba[..., 3] = cv2.GaussianBlur(rgba[..., 3], (0,0), 0.5)

# 6) Save transparent PNG
Image.fromarray(rgba, mode="RGBA").save(OUT_PNG)

# 7) (Optional) also export a simple SVG polyline
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

def contours_to_svg_path(contours, simplify_eps=2.0):
    if not contours: return ""
    cnt = max(contours, key=cv2.contourArea)
    approx = cv2.approxPolyDP(cnt, epsilon=simplify_eps, closed=False)
    if len(approx) == 0: return ""
    pts = approx.reshape(-1, 2)
    cmds = [f"M {pts[0,0]} {pts[0,1]}"] + [f"L {x} {y}" for x, y in pts[1:]]
    return " ".join(cmds)

path_d = contours_to_svg_path(contours)
if path_d:
    stroke_color = "#ffcc00"   # gold
    stroke_width = 2
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <path d="{path_d}" fill="none" stroke="{stroke_color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
'''
    Path(OUT_SVG).write_text(svg)
