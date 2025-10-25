# =============================================================
# Step2_interactive_color_picker.py
# Click on the yellow trace to automatically find its color range
# =============================================================
import cv2, numpy as np
import pydicom
from pydicom.pixel_data_handlers.util import apply_voi_lut
import matplotlib.pyplot as plt

def load_dicom_rgb(path):
    """Load DICOM as RGB uint8."""
    ds = pydicom.dcmread(path)
    try:
        arr = apply_voi_lut(ds.pixel_array, ds)
    except:
        arr = ds.pixel_array
    
    photometric = str(getattr(ds, "PhotometricInterpretation", "")).upper()
    if "MONOCHROME1" in photometric:
        arr = np.max(arr) - arr
    
    if arr.ndim == 2:
        arr = cv2.normalize(arr.astype(np.float32), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        rgb = cv2.cvtColor(arr, cv2.COLOR_GRAY2RGB)
    elif arr.ndim == 3:
        if arr.dtype != np.uint8:
            arr = cv2.normalize(arr.astype(np.float32), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        if arr.shape[-1] == 3:
            rgb = arr
        elif arr.shape[0] == 3:
            rgb = np.moveaxis(arr, 0, -1)
        else:
            rgb = arr[..., :3]
    return rgb

# Global variables for the interactive picker
selected_colors = []
img_display = None
hsv_img = None
roi_coords = None

def on_click(event, x, y, flags, param):
    """Callback for mouse clicks - collect color samples."""
    global selected_colors, img_display, hsv_img
    
    if event == cv2.EVENT_LBUTTONDOWN:
        # Get the HSV color at this point
        h, s, v = hsv_img[y, x]
        r, g, b = img_display[y, x]
        
        selected_colors.append((h, s, v))
        
        # Draw a circle to show where you clicked
        cv2.circle(img_display, (x, y), 5, (0, 255, 0), 2)
        cv2.imshow("Color Picker - Click on yellow trace (press 'q' when done)", img_display)
        
        print(f"Clicked at ({x}, {y})")
        print(f"  RGB: ({r}, {g}, {b})")
        print(f"  HSV: H={h}, S={s}, V={v}")
        print(f"  Total samples: {len(selected_colors)}")

def pick_colors_interactively(img_rgb, roi=None):
    """
    Interactive color picker - click on the trace to sample colors.
    Returns HSV lower and upper bounds.
    """
    global selected_colors, img_display, hsv_img, roi_coords
    
    selected_colors = []
    # Convert RGB to BGR for proper OpenCV display
    img_display = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    # But keep HSV conversion from RGB for correct color detection
    hsv_img = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    
    # Draw ROI box if provided
    if roi is not None:
        roi_coords = roi
        x0, y0, x1, y1 = roi
        cv2.rectangle(img_display, (x0, y0), (x1, y1), (255, 0, 0), 2)
        cv2.putText(img_display, "ROI", (x0, y0-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    
    # Create window and set mouse callback
    cv2.namedWindow("Color Picker - Click on yellow trace (press 'q' when done)")
    cv2.setMouseCallback("Color Picker - Click on yellow trace (press 'q' when done)", on_click)
    
    print("\n" + "="*60)
    print("INSTRUCTIONS:")
    print("  1. Click on MULTIPLE points along the yellow trace")
    print("  2. Click at least 5-10 points to get a good color range")
    print("  3. Press 'q' when you're done clicking")
    print("="*60 + "\n")
    
    # Show the image
    cv2.imshow("Color Picker - Click on yellow trace (press 'q' when done)", img_display)
    
    # Wait for user to finish clicking
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    
    cv2.destroyAllWindows()
    
    if len(selected_colors) == 0:
        print("No colors selected! Using your specific trace color (#FCAF17).")
        # RGB: (252, 175, 23) -> HSV in OpenCV: H≈21, S≈240, V≈252
        # Add generous padding to catch similar shades
        return np.array([15, 180, 200]), np.array([30, 255, 255])
    
    # Calculate color range from samples with padding
    h_vals = [c[0] for c in selected_colors]
    s_vals = [c[1] for c in selected_colors]
    v_vals = [c[2] for c in selected_colors]
    
    h_min, h_max = min(h_vals), max(h_vals)
    s_min, s_max = min(s_vals), max(s_vals)
    v_min, v_max = min(v_vals), max(v_vals)
    
    # Add padding to make the range more tolerant
    h_pad = 5
    s_pad = 20
    v_pad = 20
    
    lower = np.array([max(0, h_min - h_pad), 
                     max(0, s_min - s_pad), 
                     max(0, v_min - v_pad)])
    upper = np.array([min(179, h_max + h_pad), 
                     min(255, s_max + s_pad), 
                     min(255, v_max + v_pad)])
    
    print(f"\nColor range calculated from {len(selected_colors)} samples:")
    print(f"  Lower HSV: {lower}")
    print(f"  Upper HSV: {upper}")
    
    return lower, upper

def extract_trace_with_color_range(img_rgb, roi, lower_hsv, upper_hsv):
    """Extract trace using the specified HSV color range."""
    x0, y0, x1, y1 = roi
    crop = img_rgb[y0:y1, x0:x1].copy()
    
    # Convert to HSV and apply color mask
    hsv_crop = cv2.cvtColor(crop, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv_crop, lower_hsv, upper_hsv)
    
    # Clean up the mask
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    # Extract topmost pixel per column
    h, w = mask.shape
    xs, ys = [], []
    
    for x in range(w):
        col = mask[:, x]
        rows = np.where(col > 0)[0]
        if rows.size > 0:
            y_local = rows.min()  # Topmost pixel
            xs.append(x0 + x)
            ys.append(y0 + y_local)
    
    return np.array(xs), np.array(ys), mask

# ========== MAIN ==========
if __name__ == "__main__":
    import pandas as pd
    import os
    
    # Your file and ROI
    dicom_path = "./A0005"
    ROI = {'x0': 107, 'y0': 655, 'x1': 1187, 'y1': 895}
    roi = (ROI['x0'], ROI['y0'], ROI['x1'], ROI['y1'])
    
    # Load image
    img_rgb = load_dicom_rgb(dicom_path)
    print(f"Image size: {img_rgb.shape}")
    
    # STEP 1: Interactive color picking
    lower_hsv, upper_hsv = pick_colors_interactively(img_rgb, roi)
    
    # STEP 2: Extract trace using the selected color range
    xs, ys, mask = extract_trace_with_color_range(img_rgb, roi, lower_hsv, upper_hsv)
    print(f"\nExtracted {len(xs)} trace points")
    
    # STEP 3: Create clean output
    result = img_rgb.copy()
    result[roi[1]:roi[3], roi[0]:roi[2]] = 0  # Black out ROI
    
    # Draw the trace
    for x, y in zip(xs, ys):
        cv2.circle(result, (int(x), int(y)), 2, (255, 255, 0), -1)
    
    # Save outputs
    os.makedirs("interactive_output", exist_ok=True)
    cv2.imwrite("interactive_output/clean_trace.png", 
                cv2.cvtColor(result, cv2.COLOR_RGB2BGR))
    cv2.imwrite("interactive_output/mask_debug.png", mask)
    
    pd.DataFrame({"x_px": xs, "y_px": ys}).to_csv(
        "interactive_output/trace_coords.csv", index=False)
    
    # Save the color range for future use
    with open("interactive_output/color_range.txt", "w") as f:
        f.write(f"Lower HSV: {lower_hsv}\n")
        f.write(f"Upper HSV: {upper_hsv}\n")
        f.write(f"\nTo use in code:\n")
        f.write(f"lower_hsv = np.array([{lower_hsv[0]}, {lower_hsv[1]}, {lower_hsv[2]}])\n")
        f.write(f"upper_hsv = np.array([{upper_hsv[0]}, {upper_hsv[1]}, {upper_hsv[2]}])\n")
    
    # Show results
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    axes[0].imshow(img_rgb)
    axes[0].set_title("Original")
    axes[0].axis('off')
    
    axes[1].imshow(mask, cmap='gray')
    axes[1].set_title("Color Detection Mask")
    axes[1].axis('off')
    
    axes[2].imshow(result)
    axes[2].set_title("Clean Result")
    axes[2].axis('off')
    
    plt.tight_layout()
    plt.savefig("interactive_output/comparison.png", dpi=150)
    plt.show()
    
    print(f"\n✓ Outputs saved to interactive_output/")
    print(f"  Color range saved to: interactive_output/color_range.txt")

