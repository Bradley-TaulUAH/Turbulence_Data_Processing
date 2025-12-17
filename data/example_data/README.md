# Example Data

This directory contains sample datasets to demonstrate the expected CSV file formats.

## Files

### sample_centroid_tracking.csv
Example output from `Centroid tracker updated.py` showing the format for centroid tracking data:
- `frame`: Frame number from the video
- `x_centroid`: X-coordinate of the laser spot centroid (pixels)
- `y_centroid`: Y-coordinate of the laser spot centroid (pixels)
- `intensity`: Total intensity within the tracking region

This is a minimal example with just 10 frames. Real datasets typically contain thousands to tens of thousands of frames.

## Adding Your Own Examples

If you have representative datasets that would be useful as examples:
1. Make sure they're small (< 1 MB)
2. Remove any sensitive or proprietary information
3. Add them to this directory with descriptive filenames
4. Document them in this README
