"""
Display an image fullscreen for projection.
Press ESC or Q to close, or it auto-closes after a timeout.
"""
import cv2
import argparse
from pathlib import Path

def display_image(image_path, duration_seconds=None, fullscreen=False):
    """
    Display an image on screen.
    
    Args:
        image_path: Path to the image file
        duration_seconds: Auto-close after N seconds (None = wait for key press)
        fullscreen: Display fullscreen (True) or windowed (False)
    """
    # Load image
    img = cv2.imread(str(image_path))
    if img is None:
        print(f"Error: Cannot load image: {image_path}")
        return
    
    window_name = f"Projection: {Path(image_path).name}"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    if fullscreen:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    print(f"\nDisplaying: {image_path}")
    print(f"Image size: {img.shape[1]}x{img.shape[0]}")
    if duration_seconds:
        print(f"Will close after {duration_seconds} seconds")
    print("Press ESC or Q to close manually\n")
    
    cv2.imshow(window_name, img)
    
    # Wait for key press or timeout
    if duration_seconds:
        wait_time = int(duration_seconds * 1000)  # Convert to milliseconds
    else:
        wait_time = 0  # Wait indefinitely
    
    key = cv2.waitKey(wait_time)
    
    # Close if ESC (27) or Q (113) pressed
    if key in [27, 113]:
        print("Closed by user")
    elif duration_seconds:
        print(f"Auto-closed after {duration_seconds} seconds")
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Display image for projection")
    parser.add_argument("image", help="Path to image file")
    parser.add_argument("-t", "--time", type=float, default=None,
                       help="Auto-close after N seconds (default: wait for keypress)")
    parser.add_argument("-f", "--fullscreen", action="store_true",
                       help="Display fullscreen")
    
    args = parser.parse_args()
    
    display_image(args.image, args.time, args.fullscreen)


