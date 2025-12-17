# Adding Data to the Repository

This guide explains how to add your experimental CSV data files to this repository.

## Quick Answer

**You do NOT need to zip your CSV files into a single file.** 

Git works well with CSV files since they are text-based. You can add them individually or in organized folders, and they will be version-controlled properly.

## Step-by-Step Guide

### Option 1: Add Data via GitHub Web Interface (Easiest)

1. **Navigate to the repository** on GitHub: https://github.com/Bradley-TaulUAH/Turbulence_Data_Processing

2. **Go to the data directory:**
   - Click on the `data` folder
   - Choose either `raw_data/` or `processed_data/` depending on your file type

3. **Upload files:**
   - Click "Add file" → "Upload files"
   - Drag and drop your CSV files or click to browse
   - Add a commit message describing what data you're adding
   - Click "Commit changes"

### Option 2: Add Data via Git Command Line

If you have the repository cloned locally:

```bash
# Navigate to the repository
cd Turbulence_Data_Processing

# Copy your CSV files to the appropriate directory
# For example, for raw centroid data:
cp /path/to/your/data/*.csv data/raw_data/

# Or for processed SI results:
cp /path/to/your/results/*.csv data/processed_data/

# Check what files will be added
git status

# Add the new files
git add data/raw_data/*.csv
# or
git add data/processed_data/*.csv

# Commit with a descriptive message
git commit -m "Add experimental data from [date/condition]"

# Push to GitHub
git push origin main
```

### Option 3: Create a Separate Data Branch (Recommended for Large Datasets)

If you have many CSV files or want to keep data separate from code:

```bash
# Create and switch to a new branch for data
git checkout -b data/experimental-results-2024

# Add your CSV files
cp /path/to/your/data/*.csv data/raw_data/

# Commit and push
git add data/
git commit -m "Add experimental dataset from December 2024"
git push origin data/experimental-results-2024
```

Then your professor can access this branch specifically, or you can merge it into main later.

## File Organization Tips

### Organize by Experimental Condition

```
data/raw_data/
├── baseline/
│   ├── baseline_20241215_run1_centroid.csv
│   ├── baseline_20241215_run2_centroid.csv
│   └── baseline_20241216_run1_centroid.csv
├── turbulence_low/
│   ├── turbulence_low_20241215_run1_centroid.csv
│   └── turbulence_low_20241215_run2_centroid.csv
└── turbulence_high/
    ├── turbulence_high_20241216_run1_centroid.csv
    └── turbulence_high_20241216_run2_centroid.csv
```

### Organize by Date

```
data/raw_data/
├── 2024-12-15/
│   ├── baseline_run1_centroid.csv
│   ├── baseline_run2_centroid.csv
│   └── turbulence_run1_centroid.csv
└── 2024-12-16/
    ├── baseline_run1_centroid.csv
    └── turbulence_high_run1_centroid.csv
```

## What Files Should You Add?

### ✅ DO Add These Files:
- CSV files from centroid tracking (output of `Centroid tracker updated.py`)
- CSV files from SI calculations (output of `Combined centroid and intensity.py`)
- JSON metadata files with experimental parameters
- Small text files with notes or descriptions
- README files documenting your datasets

### ❌ DO NOT Add These Files:
- Original `.cine` video files (too large, 1-10 GB each)
- `.avi`, `.mp4`, or other video files
- Any other large binary files

**Note**: The `.gitignore` file automatically prevents video files from being committed, so you don't have to worry about accidentally adding them.

## File Size Considerations

- **CSV files**: Usually fine, even if several MB
- **GitHub limit**: Individual files should be < 100 MB
- **Repository size**: Try to keep total repo < 1 GB

If you have extremely large CSV files (> 50 MB), consider:
1. Splitting them into smaller files by date/condition
2. Using Git LFS (Large File Storage) - advanced option
3. Storing very large datasets elsewhere and linking to them

## Sharing Data with Your Professor

### Method 1: Share the Repository Link
Simply send your professor the repository URL:
```
https://github.com/Bradley-TaulUAH/Turbulence_Data_Processing
```

They can:
- Browse the data online
- Download individual files
- Clone the entire repository
- Download a ZIP of the entire repo using GitHub's "Code" → "Download ZIP" button

### Method 2: Share a Specific Branch
If you created a data branch:
```
https://github.com/Bradley-TaulUAH/Turbulence_Data_Processing/tree/data/experimental-results-2024
```

### Method 3: Create a Release
For a "finalized" dataset:
1. Go to repository → "Releases" → "Create a new release"
2. Tag it with a version (e.g., `v1.0-data`)
3. Add release notes describing the dataset
4. GitHub will automatically create a downloadable ZIP

## Adding Documentation with Your Data

Create a `DATASET_INFO.md` file in your data directory:

```markdown
# Dataset Information

## Experimental Setup
- Date: December 15-16, 2024
- Location: UAH Optical Lab
- Conditions tested: Baseline, Low turbulence, High turbulence

## Camera Settings
- Model: Phantom VEO 640
- Frame rate: 1000 fps
- Exposure: 100 μs
- Resolution: 2560x1600

## Beam Parameters
- Wavelength: 532 nm (green laser)
- Power: 5 mW
- Beam diameter: 5 mm
- Propagation distance: 10 m

## Files Included
- `baseline_*`: Measurements with no turbulence source
- `turbulence_low_*`: Heat gun on low setting
- `turbulence_high_*`: Heat gun on high setting

## Notes
- Run 2 on 12/15 had some tracking issues in first 100 frames
- Weather was clear, room temperature ~22°C
```

## Need Help?

If you're unsure about:
- How to organize your specific dataset
- Whether files are too large
- Which branch to use

Feel free to:
1. Add the files anyway (you can always reorganize later)
2. Open an issue on GitHub asking for advice
3. Commit to a test branch first to see how it works

## Example Workflow

Here's a complete example of adding today's data:

```bash
# 1. Make sure you're on the right branch
git checkout main
# or create a new data branch
git checkout -b data/december-2024-experiments

# 2. Create organized directories
mkdir -p data/raw_data/2024-12-17

# 3. Copy your CSV files
cp ~/experiments/today/*.csv data/raw_data/2024-12-17/

# 4. Add a description file
cat > data/raw_data/2024-12-17/README.md << EOF
# December 17, 2024 - Experiments

Turbulence measurements with varying heat gun settings.
Camera: Phantom VEO 640 at 1000 fps
Total runs: 6 (2 baseline, 2 low turbulence, 2 high turbulence)
EOF

# 5. Review what you're adding
git status
git diff --stat

# 6. Add and commit
git add data/raw_data/2024-12-17/
git commit -m "Add turbulence data from December 17, 2024

- 6 experimental runs
- Baseline, low, and high turbulence conditions
- Centroid tracking CSV files"

# 7. Push to GitHub
git push origin main
# or for a data branch:
git push origin data/december-2024-experiments
```

## Summary

- **No need to zip** - Add CSV files directly
- **Use the `data/` directory** - Organized into raw_data and processed_data
- **Be descriptive** - Use clear filenames and add README files
- **Don't worry about video files** - They're automatically excluded
- **Share via GitHub** - Your professor can access everything through the repository URL

The repository is now set up to handle your data properly!
