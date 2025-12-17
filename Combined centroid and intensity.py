import cv2
import numpy as np
from pyphantom import cine, Phantom, utils
import matplotlib.pyplot as plt
from scipy.ndimage import center_of_mass
import os
import json

def compute_tracking_aperture_si(centroid_csv_path, cine_file_path, 
                                 aperture_radius=30, edge_exclusion_percent=15,
                                 start_frame=0, end_frame=None):
    """
    Compute scintillation index using a tracking aperture that follows the centroid.
    
    This removes the geometric wander effect and isolates true scintillation.
    
    Parameters:
    -----------
    centroid_csv_path : str
        Path to CSV from centroid tracking (contains centroid_x, centroid_y columns)
    cine_file_path : str
        Path to .cine video file
    aperture_radius : int
        Radius of circular aperture (pixels) around moving centroid
    edge_exclusion_percent : int
        Exclude outer ring as percentage of aperture radius
    start_frame : int
        Frame index to start analysis
    end_frame : int or None
        Frame index to end analysis (None = use all)
    
    Returns:
    --------
    Dictionary with SI metrics and time series data
    """
    
    # Load centroid data
    print(f"[INFO] Loading centroid data from: {centroid_csv_path}")
    centroid_data = np.genfromtxt(centroid_csv_path, delimiter=',', skip_header=1, dtype=float)
    
    frame_indices = centroid_data[:, 0].astype(int)
    frame_numbers = centroid_data[:, 1].astype(int)
    centroid_x = centroid_data[:, 2]
    centroid_y = centroid_data[:, 3]
    
    if end_frame is None:
        end_frame = len(frame_indices)
    
    num_frames = end_frame - start_frame
    print(f"[INFO] Loaded {len(frame_indices)} centroid positions")
    print(f"[INFO] Analyzing frames {start_frame} to {end_frame}")
    
    # Load video
    print(f"[INFO] Loading video: {cine_file_path}")
    ph = Phantom()
    our_cine = cine.Cine.from_filepath(cine_file_path)
    
    # Create output directory
    save_dir = os.path.dirname(centroid_csv_path)
    if not save_dir:
        save_dir = "."
    
    # Compute inner radius for edge exclusion
    inner_aperture_radius = int(aperture_radius * (1.0 - edge_exclusion_percent / 100.0))
    print(f"[INFO] Aperture radius: {aperture_radius} px")
    print(f"[INFO] Inner aperture radius (excluding outer {edge_exclusion_percent}%): {inner_aperture_radius} px")
    
    # Process frames
    intensity_fixed_aperture = []
    intensity_tracking_aperture = []
    intensity_raw_centroid_region = []
    
    print(f"\n[INFO] Processing {num_frames} frames...")
    
    for idx in range(start_frame, min(end_frame, len(frame_indices))):
        if (idx - start_frame) % 100 == 0:
            print(f"[INFO] Frame {idx - start_frame + 1}/{num_frames}")
        
        frame_num = frame_numbers[idx]
        cx = centroid_x[idx]
        cy = centroid_y[idx]
        
        # Load frame
        frame = np.squeeze(our_cine.get_images(utils.FrameRange(frame_num, frame_num))).astype(np.float32)
        h, w = frame.shape[:2]
        
        # === FIXED APERTURE (baseline - geometric wander included) ===
        # Use first centroid position as reference
        cx_ref = centroid_x[start_frame]
        cy_ref = centroid_y[start_frame]
        
        Y, X = np.ogrid[:h, :w]
        dist_fixed = np.sqrt((X - cx_ref)**2 + (Y - cy_ref)**2)
        
        mask_fixed = (dist_fixed <= aperture_radius) & (dist_fixed >= 5)
        if np.any(mask_fixed):
            int_fixed = np.mean(frame[mask_fixed])
        else:
            int_fixed = np.nan
        intensity_fixed_aperture.append(int_fixed)
        
        # === TRACKING APERTURE (moving with centroid - geometric wander removed) ===
        dist_tracking = np.sqrt((X - cx)**2 + (Y - cy)**2)
        
        # Apply edge exclusion within tracking aperture
        mask_tracking = (dist_tracking <= aperture_radius) & (dist_tracking >= 5)
        
        # Additional edge exclusion for bright ring artifact
        if edge_exclusion_percent > 0:
            mask_tracking = mask_tracking & (dist_tracking <= inner_aperture_radius)
        
        if np.any(mask_tracking):
            int_tracking = np.mean(frame[mask_tracking])
        else:
            int_tracking = np.nan
        intensity_tracking_aperture.append(int_tracking)
        
        # === RAW CENTROID REGION (reference, no exclusions) ===
        dist_raw = np.sqrt((X - cx)**2 + (Y - cy)**2)
        mask_raw = dist_raw <= aperture_radius
        if np.any(mask_raw):
            int_raw = np.mean(frame[mask_raw])
        else:
            int_raw = np.nan
        intensity_raw_centroid_region.append(int_raw)
    
    # Convert to arrays and filter NaNs
    intensity_fixed_aperture = np.array(intensity_fixed_aperture)
    intensity_tracking_aperture = np.array(intensity_tracking_aperture)
    intensity_raw_centroid_region = np.array(intensity_raw_centroid_region)
    
    # Remove NaN values
    valid_idx = ~(np.isnan(intensity_fixed_aperture) | np.isnan(intensity_tracking_aperture) | np.isnan(intensity_raw_centroid_region))
    
    intensity_fixed_aperture = intensity_fixed_aperture[valid_idx]
    intensity_tracking_aperture = intensity_tracking_aperture[valid_idx]
    intensity_raw_centroid_region = intensity_raw_centroid_region[valid_idx]
    
    print(f"[INFO] Valid frames: {np.sum(valid_idx)}/{num_frames}")
    
    # Compute SI for each measurement type
    def compute_si(intensity_trace):
        """Compute scintillation index from intensity time series"""
        mean_i = np.mean(intensity_trace)
        var_i = np.var(intensity_trace)
        si = var_i / (mean_i**2 + 1e-6)
        return si
    
    si_fixed = compute_si(intensity_fixed_aperture)
    si_tracking = compute_si(intensity_tracking_aperture)
    si_raw = compute_si(intensity_raw_centroid_region)
    
    # Compute geometric contribution
    si_geometric = si_fixed - si_tracking
    
    # Print results
    print("\n" + "="*70)
    print("SCINTILLATION INDEX ANALYSIS - TRACKING vs FIXED APERTURE")
    print("="*70)
    print(f"\nFixed Aperture SI (includes geometric wander): {si_fixed:.6f}")
    print(f"Tracking Aperture SI (wander removed):        {si_tracking:.6f}")
    print(f"Raw Centroid Region SI (no edge exclusion):   {si_raw:.6f}")
    print(f"\nGeometric Wander Contribution: {si_geometric:.6f}")
    print(f"  (This is the SI increase due to fixed aperture sampling)")
    print(f"\nRatio (Fixed/Tracking): {si_fixed / (si_tracking + 1e-6):.3f}x")
    print(f"Wander % of Fixed SI: {100 * si_geometric / (si_fixed + 1e-6):.1f}%")
    print("="*70)
    
    # Create visualizations
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Plot 1: Intensity time series comparison
    ax = axes[0, 0]
    frame_indices_valid = np.arange(len(intensity_fixed_aperture))
    ax.plot(frame_indices_valid, intensity_fixed_aperture, label='Fixed Aperture', linewidth=1, alpha=0.7)
    ax.plot(frame_indices_valid, intensity_tracking_aperture, label='Tracking Aperture', linewidth=1, alpha=0.7)
    ax.fill_between(frame_indices_valid, intensity_fixed_aperture, intensity_tracking_aperture, 
                     alpha=0.2, label='Geometric Wander Effect')
    ax.set_xlabel('Frame Index', fontsize=12)
    ax.set_ylabel('Mean Intensity', fontsize=12)
    ax.set_title('Intensity Time Series: Fixed vs Tracking Aperture', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Plot 2: SI comparison bar chart
    ax = axes[0, 1]
    categories = ['Fixed\nAperture', 'Tracking\nAperture', 'Geometric\nComponent']
    values = [si_fixed, si_tracking, si_geometric]
    colors = ['#FF6B6B', '#4ECDC4', '#95E1D3']
    bars = ax.bar(categories, values, color=colors, edgecolor='black', linewidth=2)
    ax.set_ylabel('Scintillation Index', fontsize=12)
    ax.set_title('Scintillation Index Comparison', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.6f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Plot 3: Cumulative variance breakdown
    ax = axes[1, 0]
    ax.hist(intensity_fixed_aperture, bins=50, alpha=0.6, label='Fixed', edgecolor='black')
    ax.hist(intensity_tracking_aperture, bins=50, alpha=0.6, label='Tracking', edgecolor='black')
    ax.set_xlabel('Mean Intensity', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Intensity Distribution', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Plot 4: Difference time series
    ax = axes[1, 1]
    diff = intensity_fixed_aperture - intensity_tracking_aperture
    ax.plot(frame_indices_valid, diff, color='purple', linewidth=1, alpha=0.7)
    ax.fill_between(frame_indices_valid, diff, alpha=0.3, color='purple')
    ax.axhline(0, color='black', linestyle='-', linewidth=1)
    ax.axhline(np.mean(diff), color='red', linestyle='--', linewidth=2, label=f'Mean Diff: {np.mean(diff):.3f}')
    ax.set_xlabel('Frame Index', fontsize=12)
    ax.set_ylabel('Intensity Difference', fontsize=12)
    ax.set_title('Fixed - Tracking (Geometric Wander Signature)', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.suptitle('Tracking Aperture Analysis: Isolating True Scintillation', 
                 fontsize=15, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'tracking_aperture_si_analysis.png'), dpi=300, bbox_inches='tight')
    plt.show()
    
    # Save results
    results = {
        'condition': os.path.basename(centroid_csv_path).split('_')[0],
        'aperture_radius': aperture_radius,
        'edge_exclusion_percent': edge_exclusion_percent,
        'frames_analyzed': len(intensity_fixed_aperture),
        'SI': {
            'fixed_aperture': float(si_fixed),
            'tracking_aperture': float(si_tracking),
            'raw_centroid_region': float(si_raw),
            'geometric_wander_component': float(si_geometric),
            'ratio_fixed_to_tracking': float(si_fixed / (si_tracking + 1e-6))
        },
        'intensity_stats': {
            'fixed_aperture': {
                'mean': float(np.mean(intensity_fixed_aperture)),
                'std': float(np.std(intensity_fixed_aperture)),
                'min': float(np.min(intensity_fixed_aperture)),
                'max': float(np.max(intensity_fixed_aperture))
            },
            'tracking_aperture': {
                'mean': float(np.mean(intensity_tracking_aperture)),
                'std': float(np.std(intensity_tracking_aperture)),
                'min': float(np.min(intensity_tracking_aperture)),
                'max': float(np.max(intensity_tracking_aperture))
            }
        }
    }
    
    results_file = os.path.join(save_dir, 'tracking_aperture_si_results.json')
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n[INFO] Results saved to: {results_file}")
    
    # Save intensity traces as CSV for comparison
    comparison_file = os.path.join(save_dir, 'intensity_traces_comparison.csv')
    np.savetxt(comparison_file, 
               np.column_stack([frame_indices_valid, intensity_fixed_aperture, 
                              intensity_tracking_aperture, intensity_raw_centroid_region]),
               delimiter=',', 
               header='frame_index,fixed_aperture_intensity,tracking_aperture_intensity,raw_centroid_intensity',
               fmt='%d,%.6f,%.6f,%.6f')
    print(f"[INFO] Intensity traces saved to: {comparison_file}")
    
    return results


# Example usage
if __name__ == "__main__":
    from tkinter import filedialog, simpledialog, Tk
    
    # Create Tkinter root window (hidden)
    root = Tk()
    root.withdraw()
    
    # File dialogs
    print("\n[INFO] Select the centroid trajectory CSV file...")
    centroid_csv = filedialog.askopenfilename(
        title="Select Centroid Trajectory CSV File",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    
    if not centroid_csv:
        print("[ERROR] No centroid CSV file selected.")
        exit(1)
    
    print(f"[INFO] Selected: {centroid_csv}\n")
    
    print("[INFO] Select the corresponding .cine video file...")
    cine_file = filedialog.askopenfilename(
        title="Select CINE Video File",
        filetypes=[("CINE files", "*.cine"), ("All files", "*.*")]
    )
    
    if not cine_file:
        print("[ERROR] No CINE file selected.")
        exit(1)
    
    print(f"[INFO] Selected: {cine_file}\n")
    
    # Ask for aperture radius
    aperture_radius = simpledialog.askinteger(
        "Aperture Radius",
        "Enter aperture radius in pixels (default 30):",
        initialvalue=30,
        minvalue=5,
        maxvalue=200
    )
    
    if aperture_radius is None:
        aperture_radius = 30
    
    root.destroy()
    
    print(f"[INFO] Using aperture radius: {aperture_radius} pixels\n")
    
    # Run analysis
    results = compute_tracking_aperture_si(
        centroid_csv_path=centroid_csv,
        cine_file_path=cine_file,
        aperture_radius=aperture_radius,
        edge_exclusion_percent=15,
        start_frame=0,
        end_frame=None
    )
    
    print("\n" + "="*70)
    print("REPEAT THIS ANALYSIS FOR:")
    print("  - Position 4 @ Max Throttle")
    print("  - Position 3 @ Min/Max Thrust")
    print("  - Position 2 @ Min/Max Thrust")
    print("  - Compare SI_tracking across all conditions")
    print("="*70)
