# Quick Start Tutorial

This tutorial will walk you through processing your first turbulence dataset from start to finish.

## 📋 Prerequisites

Before starting, make sure you've completed [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md):
- ✅ Anaconda installed
- ✅ Phantom SDK installed and in PATH
- ✅ `turbulence` conda environment created
- ✅ All dependencies installed (`requirements.txt` + `pyphantom`)
- ✅ VS Code configured (optional but recommended)

---

## 🎯 Tutorial Overview

We'll process a complete dataset:
1. **Track centroid** of a laser spot in a `.cine` video
2. **Calculate scintillation index (SI)** using tracking aperture method
3. **Compare conditions** (e.g., control vs thrust) with histograms

**Estimated time**: 30-60 minutes (depending on video length)

---

## 📂 Prepare Your Data

### File Organization

Create a folder structure like this:

```
C:\Users\YourName\Documents\TurbulenceData\
├── Experiment_1\
│   ├── Position_X3_Control.cine
│   ├── Position_X3_Thrust.cine
│   ├── Position_X4_Control.cine
│   └── Position_X4_Thrust.cine
└── Experiment_2\
    └── ...
```

**Tips:**
- Keep control and experimental videos in the same folder
- Use descriptive filenames (include position, condition, date)
- `.cine` files are typically 1-10 GB each

---

## Step 1: Track Centroid Position

This step tracks the bright laser spot across all frames.

### 1.1 Open the Script

Using VS Code:
```bash
# In Anaconda Prompt
cd C:\Users\YourName\Documents\Turbulence_Data_Processing
code .
```

Or double-click `Centroid tracker updated.py` to open in your default editor.

### 1.2 Configure Parameters

At the bottom of `Centroid tracker updated.py`, you'll see:

```python
if __name__ == "__main__":
    results = track_centroid_across_frames(
        skip_initial_frames=300,              # ← ADJUST THIS
        dark_threshold=3000,                  # ← ADJUST THIS
        detect_ramp=True,                     
        block_size=30,
        threshold_percentile=60,              # ← ADJUST THIS
        denoise_kernel=3,
        condition_label="Position X_4 - Rolling Thrust",  # ← CHANGE THIS
        use_full_frame=False,                 
        manual_roi=(120, 110, 350, 350),      # ← ADJUST THIS
        exclude_outer_ring=True,              
        edge_exclusion_radius=None,           
        show_threshold_mask=True,             
        use_adaptive_threshold=False,         
        adaptive_block_size=31                
    )
```

**Key parameters to adjust:**

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| `skip_initial_frames` | Skip first N frames (camera settling) | 100-500 |
| `dark_threshold` | Minimum intensity to consider (filters dark frames) | 2000-5000 |
| `threshold_percentile` | Brightness threshold (higher = more selective) | 50-90 |
| `condition_label` | Descriptive name for this run | "Position_X3_Control" |
| `manual_roi` | (x, y, width, height) region to track | Adjust based on video |

**Example configurations:**

**Bright, centered laser spot:**
```python
threshold_percentile=70
manual_roi=None  # Use full frame
```

**Dim or off-center laser:**
```python
threshold_percentile=50
manual_roi=(100, 100, 400, 400)  # Restrict to region
```

**Non-uniform illumination:**
```python
use_adaptive_threshold=True
adaptive_block_size=51
```

### 1.3 Run the Script

**In VS Code:**
1. Make sure `turbulence` environment is selected (bottom-right corner)
2. Right-click in the editor → **Run Python File in Terminal**

**In Anaconda Prompt:**
```bash
conda activate turbulence
cd C:\Users\YourName\Documents\Turbulence_Data_Processing
python "Centroid tracker updated.py"
```

### 1.4 Select Your Video File

A file dialog will appear. Navigate to your `.cine` file:
```
C:\Users\YourName\Documents\TurbulenceData\Experiment_1\Position_X3_Control.cine
```

### 1.5 Enter Experiment Folder Name

When prompted, enter a folder name for outputs (e.g., `Position_X3_Control`).

All output files will be saved there.

### 1.6 Wait for Processing

You'll see progress in the console:
```
[INFO] Loading file: Position_X3_Control.cine
[INFO] Video range: 0 to 12000
[INFO] Scanning 11700 frames to filter dark frames...
[INFO] Found 10500 valid frames (above threshold)
[INFO] Analyzing intensity trace for laser ramp-up...
[INFO] Detected laser ramp at frame 450
[INFO] Creating threshold mask visualization...
[INFO] Tracking centroid across 10050 frames...
[INFO] Processing frame 1/10050
[INFO] Processing frame 101/10050
...
```

**Typical processing time:**
- 1000 frames: ~2-3 minutes
- 5000 frames: ~10-15 minutes  
- 10000 frames: ~20-30 minutes

### 1.7 Review Outputs

**Visualization Files:**
1. **`threshold_mask_visualization.png`** - **CHECK THIS FIRST!**
   - Shows what the algorithm is tracking
   - Verify the green centroid is on the laser spot
   - If wrong, adjust `threshold_percentile` or `manual_roi`

2. **`ROI_and_centroid_visualization.png`**
   - Shows initial centroid position and mean position
   - Red circle = initial position
   - Blue circle = mean position across all frames

3. **`centroid_tracking_[condition].png`**
   - 4-panel plot:
     - Top-left: X position over time
     - Top-right: Y position over time
     - Bottom-left: 2D trajectory (bird's eye view)
     - Bottom-right: Displacement magnitude

4. **`displacement_components_[condition].png`**
   - Separate X and Y displacement time series

5. **`centroid_tracking_video_[condition].mp4`**
   - Real-time visualization of tracking
   - **Watch this to verify tracking accuracy!**
   - Left side: video with centroid overlay
   - Right side: trajectory plot
   - Green circle = current position
   - Blue circle = initial position
   - Trail shows recent history

**Data Files:**
1. **`centroid_trajectory_data_[condition].csv`** - **IMPORTANT - You need this for Step 2!**
   ```csv
   frame_index,actual_frame_number,centroid_x,centroid_y,displacement_x,displacement_y,displacement_magnitude
   0,450,256.34,312.67,0.0,0.0,0.0
   1,451,256.89,312.34,0.55,-0.33,0.64
   2,452,255.98,313.12,-0.36,0.45,0.58
   ...
   ```

2. **`centroid_tracking_results_[condition].json`**
   ```json
   {
     "condition": "Position_X3_Control",
     "total_frames": 10050,
     "statistics": {
       "mean_x": 256.34,
       "mean_y": 312.67,
       "std_x": 2.45,
       "std_y": 2.89,
       "max_displacement": 12.34,
       "mean_displacement": 3.21
     },
     ...
   }
   ```

### 1.8 Interpret Results

**Console Output:**
```
==============================================================
CENTROID TRACKING RESULTS
==============================================================
Total frames tracked: 10050
Mean position: (256.34, 312.67)
Std deviation: (2.45, 2.89) pixels
Max displacement: 12.34 pixels
Mean displacement: 3.21 pixels
==============================================================
```

**What to look for:**
- **Std deviation**: Higher values = more beam wander
- **Max displacement**: Largest excursion from initial position
- **Mean displacement**: Average beam motion

**Typical values:**
- Control (no turbulence): std < 1 pixel
- Mild turbulence: std = 1-3 pixels
- Strong turbulence: std > 5 pixels

### 1.9 Repeat for Other Conditions

Now run the script again for your experimental condition:

```python
condition_label="Position_X3_Thrust"  # Change this line
```

Select the thrust video file when prompted. Use the **same ROI settings** for fair comparison.

---

## Step 2: Calculate Scintillation Index

This step computes SI using the tracking aperture method.

### 2.1 Open the Script

Open `Combined centroid and intensity.py` in VS Code or your editor.

### 2.2 Run the Script

**In VS Code:**
Right-click → **Run Python File in Terminal**

**In Anaconda Prompt:**
```bash
python "Combined centroid and intensity.py"
```

### 2.3 Select Files

**Dialog 1**: Select the centroid CSV from Step 1
```
Position_X3_Control\centroid_trajectory_data_Position_X3_Control.csv
```

**Dialog 2**: Select the corresponding `.cine` video
```
C:\Users\YourName\Documents\TurbulenceData\Experiment_1\Position_X3_Control.cine
```

**Dialog 3**: Enter aperture radius
```
Default: 30 pixels (recommended)
```
- Smaller radius (15-20): Less noise, but may miss some scintillation
- Larger radius (40-50): More averaging, smoother signal

### 2.4 Wait for Processing

```
[INFO] Loading centroid data from: centroid_trajectory_data_Position_X3_Control.csv
[INFO] Loaded 10050 centroid positions
[INFO] Analyzing frames 0 to 10050
[INFO] Loading video: Position_X3_Control.cine
[INFO] Aperture radius: 30 px
[INFO] Inner aperture radius (excluding outer 15%): 25 px

[INFO] Processing 10050 frames...
[INFO] Frame 1/10050
[INFO] Frame 101/10050
...
```

### 2.5 Review Results

**Console Output:**
```
======================================================================
SCINTILLATION INDEX ANALYSIS - TRACKING vs FIXED APERTURE
======================================================================

Fixed Aperture SI (includes geometric wander): 0.023456
Tracking Aperture SI (wander removed):        0.012345
Raw Centroid Region SI (no edge exclusion):   0.015678

Geometric Wander Contribution: 0.011111
  (This is the SI increase due to fixed aperture sampling)

Ratio (Fixed/Tracking): 1.900x
Wander % of Fixed SI: 47.4%
======================================================================
```

**Interpretation:**
- **Fixed Aperture SI**: Traditional measurement (includes beam motion)
- **Tracking Aperture SI**: True atmospheric scintillation (beam motion removed)
- **Geometric Wander**: Contribution from beam motion alone

**Key insight**: If geometric wander is large (>30% of fixed SI), beam motion is a significant confounding factor. The tracking aperture method isolates the true turbulence effect.

**Visualization Output:**

1. **`tracking_aperture_si_analysis.png`** - 4-panel plot:
   - **Top-left**: Intensity time series (fixed vs tracking aperture)
     - Gap between lines = geometric wander effect
   - **Top-right**: Bar chart comparing SI values
   - **Bottom-left**: Histogram of intensity distributions
   - **Bottom-right**: Difference time series (fixed - tracking)

**Data Files:**

1. **`intensity_traces_comparison.csv`** - **IMPORTANT - You need this for Step 3!**
   ```csv
   frame_index,fixed_aperture_intensity,tracking_aperture_intensity,raw_centroid_intensity
   0,45678.23,45890.12,45234.67
   1,46012.45,46123.34,45901.23
   ...
   ```

2. **`tracking_aperture_si_results.json`**
   ```json
   {
     "condition": "Position_X3_Control",
     "SI": {
       "fixed_aperture": 0.023456,
       "tracking_aperture": 0.012345,
       "geometric_wander_component": 0.011111
     },
     ...
   }
   ```

### 2.6 Repeat for Experimental Condition

Run the script again for your thrust condition:
- Select `Position_X3_Thrust\centroid_trajectory_data_Position_X3_Thrust.csv`
- Select the corresponding `.cine` file
- Use the **same aperture radius** for fair comparison

---

## Step 3: Generate Comparison Histograms

This step creates publication-quality histograms comparing multiple conditions.

### 3.1 Open the Script

Open `Histogram maker single video.py` in VS Code or your editor.

### 3.2 Run the Script

**In VS Code:**
Right-click → **Run Python File in Terminal**

**In Anaconda Prompt:**
```bash
python "Histogram maker single video.py"
```

### 3.3 Configure Comparison

**Dialog 1**: How many positions to compare?
```
Enter: 2 (for Position X3: Control vs Thrust)
```

**Dialog 2**: Number of bootstrap iterations
```
Default: 10000 (recommended for smooth histograms)
```

### 3.4 Select Files for Each Position

**Position 1:**
- **Label**: `Position X3 Control`
- **Distance**: `134m` (or leave blank)
- **Control file**: Select `Position_X3_Control\intensity_traces_comparison.csv`
- **Rolling thrust file**: Select `Position_X3_Thrust\intensity_traces_comparison.csv`

**Position 2 (if comparing multiple positions):**
- Repeat for Position X4, etc.

### 3.5 Wait for Processing

```
[INFO] Loading data for Position X3 Control...
[INFO] Control frames: 10050
[INFO] Rolling thrust frames: 10050
[INFO] Computing bootstrap distributions...
[INFO] Creating combined histogram...
```

**Processing time:**
- 2 positions, 10000 bootstrap iterations: ~30-60 seconds
- 4 positions, 10000 bootstrap iterations: ~2-3 minutes

### 3.6 Review Results

**Console Output:**
```
=========================================================================================
SCINTILLATION INDEX STATISTICS - TRACKING APERTURE METHOD
=========================================================================================
Position        Condition    Mean SI      Std Dev      95% CI
-----------------------------------------------------------------------------------------
Position X3     Control      0.012345     0.000234     [0.012100, 0.012590]
                Rolling      0.023456     0.000456     [0.022900, 0.024012]
                Increase     +90.05%
-----------------------------------------------------------------------------------------
Position X4     Control      0.015678     0.000289     [0.015400, 0.015956]
                Rolling      0.034567     0.000678     [0.033500, 0.035634]
                Increase     +120.45%
-----------------------------------------------------------------------------------------
=========================================================================================
```

**Interpretation:**
- **Mean SI**: Average scintillation index (higher = more turbulence)
- **95% CI**: Confidence interval (narrow = more precise measurement)
- **Increase**: Percent increase from control to thrust condition

**Visualization Output:**

1. **`si_histogram_all_positions.png`**
   - 2x2 grid (if 4 positions) or fewer panels
   - Each panel shows overlapping histograms:
     - Gray = Control (background)
     - Purple = Rolling thrust
   - Dashed vertical lines = mean values
   - Text box shows statistics and % increase

**Typical Results:**
- Turbulence from thrust increases SI by 50-200%
- Closer positions (stronger turbulence) show larger increases
- Histograms should have good overlap (indicates similar measurement conditions)

---

## 🎓 Example Workflow Summary

Here's a complete example processing **Position X3** with control and thrust:

```bash
# Activate environment
conda activate turbulence
cd C:\Users\YourName\Documents\Turbulence_Data_Processing

# Step 1a: Track centroid - Control condition
# Edit condition_label="Position_X3_Control" in script
python "Centroid tracker updated.py"
# → Select Position_X3_Control.cine
# → Output: Position_X3_Control\centroid_trajectory_data_Position_X3_Control.csv

# Step 1b: Track centroid - Thrust condition
# Edit condition_label="Position_X3_Thrust" in script
python "Centroid tracker updated.py"
# → Select Position_X3_Thrust.cine
# → Output: Position_X3_Thrust\centroid_trajectory_data_Position_X3_Thrust.csv

# Step 2a: Calculate SI - Control condition
python "Combined centroid and intensity.py"
# → Select centroid_trajectory_data_Position_X3_Control.csv
# → Select Position_X3_Control.cine
# → Aperture radius: 30
# → Output: Position_X3_Control\intensity_traces_comparison.csv

# Step 2b: Calculate SI - Thrust condition
python "Combined centroid and intensity.py"
# → Select centroid_trajectory_data_Position_X3_Thrust.csv
# → Select Position_X3_Thrust.cine
# → Aperture radius: 30
# → Output: Position_X3_Thrust\intensity_traces_comparison.csv

# Step 3: Generate histogram comparison
python "Histogram maker single video.py"
# → Number of positions: 1
# → Bootstrap iterations: 10000
# → Position 1 label: "Position X3"
# → Distance: "134m"
# → Select Position_X3_Control\intensity_traces_comparison.csv (control)
# → Select Position_X3_Thrust\intensity_traces_comparison.csv (thrust)
# → Output: si_histogram_all_positions.png
```

---

## 🔍 Quality Control Checklist

Before trusting your results, verify:

### Step 1 (Centroid Tracking):
- [ ] `threshold_mask_visualization.png` shows centroid on laser spot
- [ ] `centroid_tracking_video.mp4` shows stable tracking (no jumps)
- [ ] Std deviation is reasonable (<10 pixels for typical setups)
- [ ] ROI encompasses the entire laser spot motion range

### Step 2 (SI Calculation):
- [ ] Intensity time series doesn't have large gaps or spikes
- [ ] Fixed aperture SI > Tracking aperture SI (expected)
- [ ] Geometric wander component is positive
- [ ] Histogram shows smooth distribution (not choppy)

### Step 3 (Comparison):
- [ ] Control SI < Thrust SI (if thrust causes turbulence)
- [ ] Bootstrap histograms are smooth (not jagged)
- [ ] 95% CI ranges don't overlap excessively (if expecting significant difference)
- [ ] Text box statistics match console output

---

## 🛠️ Troubleshooting Common Issues

### Issue 1: Centroid jumps around erratically

**Symptoms**: Video shows centroid jumping to random locations

**Solutions:**
```python
# 1. Increase threshold (more selective)
threshold_percentile=80  # Higher = more selective

# 2. Restrict to smaller ROI
manual_roi=(150, 150, 300, 300)  # Tighter region

# 3. Enable edge exclusion
exclude_outer_ring=True
edge_exclusion_radius=50  # Exclude outer 50 pixels
```

### Issue 2: "No valid frames found"

**Symptoms**: Script exits with error after frame filtering

**Solutions:**
```python
# Lower dark threshold
dark_threshold=1000  # Try lower values

# Disable ramp detection
detect_ramp=False
```

### Issue 3: Histogram shows no difference between conditions

**Symptoms**: Control and thrust histograms completely overlap

**Possible causes:**
- Turbulence effect is genuinely small
- Wrong files selected (both are same condition)
- Aperture radius too large (averaging out fluctuations)

**Solutions:**
```python
# Reduce aperture radius for more sensitivity
aperture_radius=20  # Smaller = more sensitive to fluctuations
```

### Issue 4: SI values seem unreasonably high (>0.5)

**Possible causes:**
- Beam is clipped at aperture edges
- Background noise is high
- ROI is too small

**Solutions:**
```python
# Increase aperture radius
aperture_radius=40  # Ensure spot is fully captured

# Increase edge exclusion
edge_exclusion_percent=20  # Exclude more of outer ring
```

---

## 📊 Interpreting Your Results

### Scintillation Index Ranges

| SI Value | Turbulence Strength | Typical Conditions |
|----------|---------------------|-------------------|
| 0.001 - 0.01 | Weak | Clear air, minimal turbulence |
| 0.01 - 0.05 | Moderate | Natural atmospheric turbulence |
| 0.05 - 0.2 | Strong | Heat plumes, jet exhaust |
| > 0.2 | Very Strong | Near-field turbulence, saturation regime |

### Expected Trends

**Distance dependence:**
- SI typically increases with propagation distance
- Longer paths accumulate more turbulence

**Thrust/turbulence source:**
- SI should increase when turbulence source is active
- Increase of 50-200% is typical for strong sources

**Geometric wander:**
- Should be 20-50% of fixed aperture SI for typical setups
- Higher values indicate significant beam motion

---

## 🎯 Next Steps

Now that you've processed your first dataset:

1. **Process multiple positions** to study spatial variation
2. **Compare different experimental conditions** (thrust levels, distances, etc.)
3. **Statistical analysis**: Use the CSV files for time-series analysis in Excel/MATLAB/Python
4. **Publication figures**: The PNG outputs are high-resolution (300 DPI) and ready for papers

---

## 📚 Additional Resources

- **README.md**: Overview and feature list
- **ENVIRONMENT_SETUP.md**: Detailed installation guide
- **requirements.txt**: Python package versions
- **GitHub Issues**: Report bugs or ask questions

---

## 💡 Tips for Efficient Processing

1. **Batch processing**: Modify scripts to loop over multiple files
2. **Parameter tuning**: Save configurations for each position in comments
3. **Organize outputs**: Create subfolders for each experimental condition
4. **Backup data**: Keep original `.cine` files separate from processed results
5. **Documentation**: Record ROI coordinates and parameters in a lab notebook

---

**Congratulations!** You've completed your first turbulence data processing workflow. 🎉

For questions or issues, please open an issue on the GitHub repository.
