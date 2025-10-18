# Doppler Ultrasound Time-Series Extraction

Extract velocity time-series from spectral Doppler ultrasound images.

## What it does
- **Snapshot (DICOM still)**: Extract velocity envelope from a single spectral Doppler image
- **Video (WMV/MP4/multi-frame DICOM)**: Extract velocity envelopes from scrolling spectrogram at time intervals

## Quick Start

### 1. Setup Data Folders
The data files are **not included** in this repository (too large for GitHub). You need to provide your own data:

- Create a `DICOM/` folder and place your DICOM files there
  - Example structure: `DICOM/Artery/at_1_1`, `DICOM/Sup_arm_vein/A0000`, etc.
- Create a `Converted_files/` folder for video files
  - Example structure: `Converted_files/Vein/Vein_cont.wmv`, etc.

### 2. Run the Notebook
1. Open `dicom_to_ts.ipynb`
2. **IMPORTANT**: Restart the kernel (Kernel → Restart) to clear old code
3. Run the **Setup** cell first (creates `output/` folder and helper functions)
4. Edit file paths in the processing cells to match your data location
5. Run the cells for snapshot or video processing
6. Find results in `output/` folder

## Outputs
All results saved to `output/`:
- **CSV files**: `time_s, velocity_cm_s` columns
- **PNG plots**: spectrograms + velocity curves

## How it Works
1. Crops the spectral Doppler panel from the ultrasound image
2. Auto-detects the baseline (zero-velocity line)
3. Auto-calibrates pixel-to-velocity scale from grid lines
4. Extracts the bright envelope (max velocity at each time point)
5. Smooths and exports as time-series

## Configuration
Adjust these in the processing cells if needed:
- **Crop ratios**: `CROP_X1, CROP_X2, CROP_Y1, CROP_Y2` (default works for most machines)
- **Time span**: `TIME_SPAN_S` (seconds shown in spectral box)
- **Calibration**: `TICK_VALUE_CM_S` (velocity per grid tick, usually 10 or 20 cm/s)
- **Video**: `WINDOW_INTERVAL_S` (extract envelope every N seconds)

## Export to HTML

### Simple method (recommended)
Run the export script:
```bash
.\dus\Scripts\python.exe export_html.py
```
This creates `output/dicom_to_ts.html` - open it in any web browser.

### Alternative: From Jupyter Notebook
In the notebook menu: **File → Download as → HTML (.html)**  
(This may not work if nbconvert templates aren't installed - use the script above instead)

## Dependencies
All required packages are in the `dus/` virtual environment:
- `pydicom` - DICOM reading
- `numpy` - array processing
- `matplotlib` - plotting
- `imageio` / `opencv-python` - video reading


