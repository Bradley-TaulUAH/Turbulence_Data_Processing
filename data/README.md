# Turbulence Data Directory

This directory contains experimental data collected using the Turbulence Data Processing Toolkit.

## Directory Structure

```
data/
├── README.md           # This file
├── raw_data/           # Raw centroid tracking CSV files
├── processed_data/     # Processed scintillation index results
└── example_data/       # Example datasets for testing and demonstration
```

## Data Organization

### raw_data/
Contains raw centroid tracking data (output from `Centroid tracker updated.py`):
- CSV files with columns: frame, x_centroid, y_centroid, intensity
- Naming convention: `[condition]_[date]_centroid.csv`
- Example: `baseline_20241215_centroid.csv`

### processed_data/
Contains processed scintillation index results (output from `Combined centroid and intensity.py`):
- CSV files with SI calculations for both fixed and tracking aperture methods
- Naming convention: `[condition]_[date]_SI_results.csv`
- Example: `baseline_20241215_SI_results.csv`

### example_data/
Contains sample datasets for testing and demonstration purposes.

## Adding Your Data

To add your experimental data to this repository:

1. **Organize your files** by experimental condition or date
2. **Place raw centroid CSVs** in the `raw_data/` directory
3. **Place processed SI results** in the `processed_data/` directory
4. **Use descriptive filenames** that indicate:
   - Experimental condition (e.g., baseline, thrust_on, turbulence)
   - Date (YYYYMMDD format)
   - Type of data (centroid, SI_results, etc.)

## File Naming Best Practices

Use clear, descriptive names that include:
- **Condition**: What was different in this experiment
- **Date**: When the data was collected (YYYYMMDD)
- **Type**: What kind of data this is

Examples:
- `baseline_no_turbulence_20241215_centroid.csv`
- `jet_exhaust_high_thrust_20241215_SI_results.csv`
- `natural_atmospheric_20241216_centroid.csv`

## Data Documentation

When adding new datasets, consider creating a corresponding metadata file or updating this README with:
- Experimental conditions
- Camera settings (frame rate, exposure, etc.)
- Environmental conditions
- Beam parameters
- Any notes or observations

## Large Files

**Important**: Do NOT commit large binary files (`.cine` video files):
- Original `.cine` files are typically 1-10 GB
- Store these separately (external drive, cloud storage, etc.)
- Only commit the processed CSV outputs
- The `.gitignore` file prevents accidental commits of video files

## CSV File Format

### Centroid Tracking CSV
```csv
frame,x_centroid,y_centroid,intensity
0,512.34,384.56,15234.5
1,512.45,384.61,15198.3
...
```

### SI Results CSV
Varies based on processing script output, but typically includes:
- Frame information
- Fixed aperture SI values
- Tracking aperture SI values
- Statistical measures (mean, variance, etc.)

## Questions?

See the main [README.md](../README.md) for more information about the processing toolkit.
