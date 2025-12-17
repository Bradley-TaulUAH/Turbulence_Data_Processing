# Quick Instructions: Adding Your CSV Data to the Repository

## Your Question Answered

> "Can we make a new branch so that I can send my professor the csv of all of the data I took and put that into the repo would I have to put them all in a single file then zip that file or how do I do that?"

**Short Answer:** 
- ✅ **NO, you do NOT need to zip your CSV files**
- ✅ You can add them directly to the repository
- ✅ Git handles CSV files perfectly (they're just text files)
- ✅ We've created a `data/` directory structure for you

## Three Simple Ways to Add Your Data

### Method 1: Using GitHub Website (Easiest!)

1. Go to https://github.com/Bradley-TaulUAH/Turbulence_Data_Processing
2. Click on the `data` folder, then `raw_data`
3. Click "Add file" → "Upload files"
4. Drag and drop all your CSV files (you can select multiple files at once)
5. Write a message like "Add experimental data from December 2024"
6. Click "Commit changes"

**That's it!** Your professor can now access all the files by visiting the repository.

### Method 2: Using Git on Your Computer

If you have the repository on your computer:

```bash
# Navigate to the repository
cd Turbulence_Data_Processing

# Copy your CSV files (all at once!)
cp /path/to/your/data/*.csv data/raw_data/

# Add them to git
git add data/raw_data/*.csv

# Commit with a message
git commit -m "Add my experimental data CSV files"

# Push to GitHub
git push
```

### Method 3: Create a Dedicated Data Branch (Optional)

If you want to keep your data separate:

```bash
# Create a new branch just for data
git checkout -b my-experimental-data

# Add your CSV files
cp /path/to/your/data/*.csv data/raw_data/

# Commit and push
git add data/
git commit -m "Add all experimental CSV data"
git push origin my-experimental-data
```

Then send your professor this link:
```
https://github.com/Bradley-TaulUAH/Turbulence_Data_Processing/tree/my-experimental-data
```

## How to Share with Your Professor

### Option A: Send the Repository Link
Just send:
```
https://github.com/Bradley-TaulUAH/Turbulence_Data_Processing
```

Your professor can:
- View all files online
- Download individual CSVs by clicking on them
- Download everything as a ZIP using "Code" → "Download ZIP"
- Clone the whole repository

### Option B: Send a Direct Link to the Data Folder
```
https://github.com/Bradley-TaulUAH/Turbulence_Data_Processing/tree/main/data
```

### Option C: Create a Release (For Final Datasets)
1. Go to repository → "Releases" → "Create a new release"
2. Tag it as "v1.0-data" or similar
3. Write a description of what data is included
4. Publish release
5. GitHub creates a downloadable ZIP automatically

## What Files to Add

### ✅ YES - Add These:
- All your CSV files from centroid tracking
- CSV files from scintillation index calculations
- Any notes or documentation (as .txt or .md files)

### ❌ NO - Don't Add These:
- Original video files (.cine, .avi, .mp4) - they're too large
- The `.gitignore` file we created prevents this automatically

## Organization Tips

You can organize your CSVs however makes sense to you:

**By date:**
```
data/raw_data/
├── 2024-12-15_baseline_run1.csv
├── 2024-12-15_baseline_run2.csv
├── 2024-12-16_turbulence_run1.csv
└── 2024-12-16_turbulence_run2.csv
```

**By condition:**
```
data/raw_data/
├── baseline_experiment1.csv
├── baseline_experiment2.csv
├── low_turbulence_experiment1.csv
└── high_turbulence_experiment1.csv
```

**Or just dump them all in:**
```
data/raw_data/
├── data1.csv
├── data2.csv
├── data3.csv
└── data4.csv
```

All work fine! Choose what makes most sense for your data.

## Important Notes

1. **File size**: CSV files are usually fine even if they're several MB. GitHub allows files up to 100 MB.

2. **Multiple files**: You can add as many CSV files as you want - no need to combine them.

3. **No special tools needed**: You can use the GitHub website - no need to learn command line git if you don't want to.

4. **Already protected**: The `.gitignore` file prevents you from accidentally adding huge video files.

## Need More Details?

See [DATA_GUIDE.md](DATA_GUIDE.md) for comprehensive instructions with examples.

## Summary

1. **Don't zip your CSVs** - add them directly
2. **Use the GitHub website** if you're not comfortable with command line
3. **Put files in `data/raw_data/`** directory
4. **Send your professor the repository link**

The repository is ready for your data!
