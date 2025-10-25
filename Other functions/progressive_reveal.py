"""
Progressive image reveal - black screen that reveals image left to right
Like a loading/generation animation
"""
import cv2
import numpy as np
import time
from pathlib import Path

def progressive_reveal(image_path, duration_seconds=60, fullscreen=False):
    """
    Show a black screen that progressively reveals the image from left to right.
    
    Args:
        image_path: Path to the image
        duration_seconds: How long the full reveal takes (default 60s)
        fullscreen: Display fullscreen for projection
    """
    # Load image
    img = cv2.imread(str(image_path))
    if img is None:
        print(f"Error: Cannot load image: {image_path}")
        return
    
    height, width = img.shape[:2]
    
    # Create window
    window_name = "Generating Image..."
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    if fullscreen:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    print(f"\nRevealing: {image_path}")
    print(f"Duration: {duration_seconds} seconds")
    print("Press ESC to skip animation\n")
    
    # Start with black screen
    black = np.zeros_like(img)
    
    # Calculate timing
    fps = 60  # Smooth animation at 60 fps
    total_frames = int(duration_seconds * fps)
    pixels_per_frame = width / total_frames
    
    start_time = time.time()
    
    for frame in range(total_frames + 1):
        # Calculate how much of the image to reveal
        reveal_width = int(frame * pixels_per_frame)
        reveal_width = min(reveal_width, width)  # Don't exceed image width
        
        # Create the progressive reveal
        display = black.copy()
        if reveal_width > 0:
            display[:, :reveal_width] = img[:, :reveal_width]
        
        # Show the frame
        cv2.imshow(window_name, display)
        
        # Check for ESC key to skip
        key = cv2.waitKey(1)
        if key == 27:  # ESC
            print("Animation skipped by user")
            # Show full image immediately
            cv2.imshow(window_name, img)
            cv2.waitKey(2000)  # Show for 2 seconds
            break
        
        # Control frame rate
        elapsed = time.time() - start_time
        expected_time = frame / fps
        sleep_time = expected_time - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)
    
    else:
        # Animation completed, show full image for a moment
        print("Reveal complete!")
        cv2.imshow(window_name, img)
        cv2.waitKey(2000)  # Hold final image for 2 seconds
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Progressive image reveal animation")
    parser.add_argument("image", help="Path to image file")
    parser.add_argument("-t", "--time", type=int, default=60,
                       help="Reveal duration in seconds (default: 60)")
    parser.add_argument("-f", "--fullscreen", action="store_true",
                       help="Display fullscreen")
    
    args = parser.parse_args()
    
    progressive_reveal(args.image, args.time, args.fullscreen)


