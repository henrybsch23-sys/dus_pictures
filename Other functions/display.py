import time, math, random
from pathlib import Path
import numpy as np
import cv2
import matplotlib.pyplot as plt

# ---------- CONFIG ----------
IMG_PATH = "pic_1.jpg"     # <— change to your file
DURATION = 30.0                 # seconds
FPS = 60                        # target frame rate
STYLE = "wipe"                  # "wipe" | "blur_to_sharp" | "random_tiles"
TILE_SIZE = 32                  # for "random_tiles"
MAX_SIGMA = 15                  # for "blur_to_sharp"
# ----------------------------

# Load image (as RGB)
img_bgr = cv2.imread(IMG_PATH, cv2.IMREAD_COLOR)
if img_bgr is None:
    raise FileNotFoundError(f"Couldn't read {IMG_PATH}")
img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
H, W = img.shape[:2]

def frame_wipe(img, frac):
    """Left-to-right wipe."""
    out = np.zeros_like(img)
    x_cut = int(frac * W)
    out[:, :x_cut] = img[:, :x_cut]
    return out

def frame_blur_to_sharp(img, frac):
    """Starts very blurry and sharpens to original."""
    sigma = MAX_SIGMA * (1.0 - frac)
    k = max(3, int(2 * round(3*sigma) + 1))  # odd kernel (approx 3σ)
    if sigma < 0.3:
        return img.copy()
    blurred = cv2.GaussianBlur(img, (k, k), sigmaX=sigma, sigmaY=sigma, borderType=cv2.BORDER_REPLICATE)
    # cross-fade blurred -> sharp
    return (blurred.astype(np.float32) * (1-frac) + img.astype(np.float32) * frac).astype(np.uint8)

def frame_random_tiles(img, frac):
    """Reveals random tiles over time."""
    th, tw = TILE_SIZE, TILE_SIZE
    grid_y = math.ceil(H / th)
    grid_x = math.ceil(W / tw)
    total = grid_x * grid_y

    # cache permutation on first call
    if not hasattr(frame_random_tiles, "_perm"):
        idxs = list(range(total))
        random.seed(0)
        random.shuffle(idxs)
        frame_random_tiles._perm = idxs

    n_show = int(frac * total)
    mask = np.zeros((H, W), np.uint8)
    for k in frame_random_tiles._perm[:n_show]:
        gy, gx = divmod(k, grid_x)
        y0, y1 = gy*th, min((gy+1)*th, H)
        x0, x1 = gx*tw, min((gx+1)*tw, W)
        mask[y0:y1, x0:x1] = 255

    out = np.zeros_like(img)
    out[mask == 255] = img[mask == 255]
    return out

def make_frame(img, frac):
    frac = max(0.0, min(1.0, frac))
    if STYLE == "wipe":
        return frame_wipe(img, frac)
    elif STYLE == "blur_to_sharp":
        return frame_blur_to_sharp(img, frac)
    elif STYLE == "random_tiles":
        return frame_random_tiles(img, frac)
    else:
        return frame_wipe(img, frac)

# --- Live window animation (~30 s) ---
plt.ion()
fig, ax = plt.subplots()
fig.canvas.manager.set_window_title("Image Generation Demo")
ax.axis("off")
im = ax.imshow(np.zeros_like(img))  # placeholder

start = time.perf_counter()
frame_time = 1.0 / FPS

while True:
    elapsed = time.perf_counter() - start
    frac = elapsed / DURATION
    if frac >= 1.0:
        im.set_data(img)
        fig.canvas.draw()
        plt.pause(0.001)
        break

    out = make_frame(img, frac)
    im.set_data(out)
    fig.canvas.draw()
    # Keep timing close to 30s regardless of render cost
    target_next = start + min(elapsed + frame_time, DURATION)
    sleep_for = max(0.0, target_next - time.perf_counter())
    plt.pause(sleep_for)

# Keep window open until closed
plt.ioff()
plt.show()
