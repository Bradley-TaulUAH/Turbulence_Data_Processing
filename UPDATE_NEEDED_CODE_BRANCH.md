# Instructions to Update needed-code Branch

The Python files and requirements.txt have been prepared and are ready to be added to the `needed-code` branch.

## Current Status

✅ The `copilot/add-python-and-text-files` branch contains:
- All existing files from `needed-code`
- **Histogram maker single video.py** (NEW - 10,191 bytes)
- **requirements.txt** (NEW - 299 bytes)

## Option 1: Fast-Forward Merge (Recommended)

Run these commands to update the `needed-code` branch:

```bash
git fetch origin
git checkout needed-code
git merge --ff-only origin/copilot/add-python-and-text-files
git push origin needed-code
```

## Option 2: Direct Branch Update

If you want to directly update `needed-code` to match `copilot/add-python-and-text-files`:

```bash
git fetch origin
git checkout needed-code
git reset --hard origin/copilot/add-python-and-text-files
git push --force origin needed-code
```

## Option 3: Using GitHub Web UI

1. Go to: https://github.com/Bradley-TaulUAH/Turbulence_Data_Processing
2. Navigate to Pull Requests
3. Find PR #2
4. Change the base branch from `main` to `needed-code`
5. Merge the PR

## Files Added

### Histogram maker single video.py
- Complete histogram generation script with bootstrap SI distribution analysis
- 278 lines of Python code
- Includes functions for:
  - Bootstrap SI distribution calculation
  - Intensity trace loading
  - Histogram plotting with confidence intervals

### requirements.txt
- 18 Python package dependencies:
  - av==14.1.0
  - numpy==1.26.4
  - opencv-python==4.10.0.84
  - matplotlib==3.10.0
  - pandas==2.2.3
  - scipy==1.14.1
  - And 12 more dependencies

## Verification

After updating `needed-code`, verify with:

```bash
git checkout needed-code
ls -la *.py *.txt
```

You should see 7 files total:
- Centroid tracker updated.py
- Combined centroid and intensity.py
- Histogram maker single video.py ← NEW
- requirements.txt ← NEW
- Plus documentation files
