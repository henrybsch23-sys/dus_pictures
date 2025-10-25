#!/usr/bin/env python3
"""
plot_csv.py
--------------------
Open a waveform CSV file and plot the time-series.
If the CSV has columns 'time_s' and 'velocity_cm_s', it will plot those directly.
Otherwise, it will just show whatever numeric columns exist.
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# === CONFIG ===
CSV_PATH = Path("combined_lines.csv")  # your CSV file
OUT_PLOT = Path("waveform_plot.png")        # output image file
# ==============

# 1) Load CSV
df = pd.read_csv(CSV_PATH)
print(f"✅ Loaded {CSV_PATH} with {len(df)} rows and columns: {list(df.columns)}")

# 2) Determine what to plot
if {"time_s", "velocity_cm_s"}.issubset(df.columns):
    x = df["time_s"]
    y = df["velocity_cm_s"]
    xlabel, ylabel = "Time (s)", "Velocity (cm/s)"
elif len(df.columns) >= 2:
    # fallback: first two numeric columns
    numeric_cols = df.select_dtypes(include=["number"]).columns
    if len(numeric_cols) < 2:
        raise ValueError("No numeric columns to plot.")
    x, y = df[numeric_cols[0]], df[numeric_cols[1]]
    xlabel, ylabel = numeric_cols[0], numeric_cols[1]
else:
    raise ValueError("CSV missing numeric data to plot.")

# 3) Plot
plt.figure(figsize=(10, 4))
plt.plot(x, y, color="dodgerblue", linewidth=2)
plt.title("Waveform Time Series")
plt.xlabel(xlabel)
plt.ylabel(ylabel)
plt.grid(True, alpha=0.35)
plt.tight_layout()
plt.savefig(OUT_PLOT, dpi=150)
plt.show()

print(f"📊 Plot saved as {OUT_PLOT.resolve()}")
