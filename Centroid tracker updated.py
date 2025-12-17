import cv2
import numpy as np
from pyphantom import cine, Phantom, utils
import matplotlib.pyplot as plt
from scipy.ndimage import center_of_mass
import os
import json

def get_experiment_folder():
    """Create a folder for saving experiment results"""
    exp_name = input("Enter a unique name for this experiment/folder (or press Enter for 'centroid_tracking'): ").strip()
    if not exp_name:
        exp_name = "centroid_tracking"
    dirname = exp_name.replace(" ", "_")
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return dirname

def extract_roi_intensity(frame, roi_size=20):
    """Extract intensity from brightest region of frame"""
    frame_denoised = cv2.medianBlur(frame, 3)
    threshold = np.percentile(frame_denoised, 90)
    mask = frame_denoised > threshold
    if np.any(mask):
        cy, cx = center_of_mass(mask)
    else:
        cy, cx = frame.shape[0] // 2, frame.shape[1] // 2
    
    y1, y2 = int(cy - roi_size), int(cy + roi_size)
    x1, x2 = int(cx - roi_size), int(cx + roi_size)
    roi = frame[max(0, y1):min(frame.shape[0], y2), max(0, x1):min(frame.shape[1], x2)]
    return np.sum(roi)

def find_ramp_blocks(block_means, threshold_ratio=1.5, min_step=30000):
    """Detect when laser ramps up (turns on)"""
    diffs = np.diff(block_means)
    ramp_start = None
    ramp_end = None
    
    for i, d in enumerate(diffs):
        if d > min_step and (block_means[i+1] > threshold_ratio * np.median(block_means[:i+1])):
            ramp_start = i + 1
            break
    
    if ramp_start is not None:
        for j in range(ramp_start + 1, len(diffs)):
            if abs(diffs[j]) < (0.1 * np.median(abs(diffs[max(0, ramp_start-5):ramp_start+1]))):
                ramp_end = j + 1
                break
    
    return ramp_start, ramp_end

def filter_dark_frames(our_cine, start, end, dark_threshold=5000):
    """Filter out dark frames and return valid frame numbers with intensities"""
    print(f"[INFO] Scanning {end - start + 1} frames to filter dark frames...")
    
    intensity_trace = []
    frame_numbers_valid = []
    
    for framenum in range(start, end + 1):
        frame = np.squeeze(our_cine.get_images(utils.FrameRange(framenum, framenum)))
        
        if frame.ndim > 2:
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            frame_gray = frame.astype(np.uint8) if frame.dtype != np.uint8 else frame
        
        intensity = extract_roi_intensity(frame_gray)
        
        if intensity < dark_threshold:
            continue
        
        intensity_trace.append(intensity)
        frame_numbers_valid.append(framenum)
    
    print(f"[INFO] Found {len(frame_numbers_valid)} valid frames (above threshold)")
    return frame_numbers_valid, intensity_trace

def compute_centroid(frame, threshold_percentile=90, exclude_edges=True, edge_exclusion_radius=None, frame_center=None, use_adaptive_threshold=False, adaptive_block_size=51):
    """
    Compute the center of mass (centroid) of the brightest region in the frame.
    Returns (cx, cy) coordinates.
    
    Parameters:
    -----------
    frame : np.ndarray
        Input frame
    threshold_percentile : float
        Percentile threshold for bright region detection (used if use_adaptive_threshold=False)
    exclude_edges : bool
        Whether to exclude edge regions from centroid calculation
    edge_exclusion_radius : int or None
        Radius from frame edges to exclude (if None, auto-calculated)
    frame_center : tuple or None
        (cx, cy) center of frame for circular exclusion
    use_adaptive_threshold : bool
        If True, uses adaptive thresholding instead of percentile
    adaptive_block_size : int
        Block size for adaptive thresholding (must be odd, larger = smoother)
    """
    frame_denoised = cv2.medianBlur(frame, 3)
    
    # Create mask to exclude edges
    if exclude_edges:
        h, w = frame.shape
        mask_exclude = np.ones_like(frame, dtype=bool)
        
        if edge_exclusion_radius is None:
            # Auto-calculate: exclude outer 15% of radius
            edge_exclusion_radius = int(min(w, h) * 0.15)
        
        if frame_center is None:
            frame_center = (w // 2, h // 2)
        
        # Create circular mask to exclude outer ring
        Y, X = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((X - frame_center[0])**2 + (Y - frame_center[1])**2)
        max_radius = min(frame_center[0], frame_center[1], 
                        w - frame_center[0], h - frame_center[1])
        inner_radius = max_radius - edge_exclusion_radius
        
        # Exclude outer ring
        mask_exclude = dist_from_center < inner_radius
        
        # Apply mask
        frame_masked = frame_denoised.copy()
        frame_masked[~mask_exclude] = 0
    else:
        frame_masked = frame_denoised
        mask_exclude = np.ones_like(frame, dtype=bool)
    
    # Apply thresholding
    if use_adaptive_threshold:
        # Adaptive thresholding - better for non-uniform illumination
        # Normalize frame to 8-bit
        frame_8bit = cv2.normalize(frame_masked, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
        # Apply adaptive threshold
        # Using Gaussian method which considers weighted neighborhood
        threshold_mask = cv2.adaptiveThreshold(
            frame_8bit, 
            255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            adaptive_block_size,  # Block size (must be odd)
            -10  # Constant subtracted from weighted mean (negative = more permissive)
        )
        
        mask = (threshold_mask > 0) & mask_exclude
    else:
        # Global percentile threshold
        threshold = np.percentile(frame_masked[frame_masked > 0], threshold_percentile)
        mask = (frame_masked > threshold) & mask_exclude
    
    if np.any(mask):
        cy, cx = center_of_mass(mask)
        return (cx, cy)
    else:
        # Return frame center if no bright region found
        return (frame.shape[1] / 2.0, frame.shape[0] / 2.0)

def track_centroid_across_frames(
    skip_initial_frames=0,
    dark_threshold=5000,
    detect_ramp=True,
    block_size=30,
    threshold_percentile=90,
    denoise_kernel=3,
    condition_label="Condition",
    use_full_frame=True,
    manual_roi=None,  # (x, y, w, h) tuple if you want to restrict tracking to ROI
    exclude_outer_ring=True,  # NEW: Exclude bright outer ring
    edge_exclusion_radius=None,  # NEW: Radius to exclude (pixels from edge)
    show_threshold_mask=True,  # NEW: Visualize what the algorithm "sees"
    use_adaptive_threshold=False,  # NEW: Use adaptive thresholding for non-uniform illumination
    adaptive_block_size=51  # NEW: Block size for adaptive threshold
):
    """
    Track the center of mass (centroid) of a bright spot across frames.
    
    Parameters:
    -----------
    skip_initial_frames : int
        Number of initial frames to skip
    dark_threshold : float
        Threshold to filter out dark frames
    detect_ramp : bool
        Whether to detect laser ramp-up
    block_size : int
        Block size for ramp detection
    threshold_percentile : float
        Percentile threshold for identifying bright region (90 = top 10% brightest)
        Only used if use_adaptive_threshold=False
    denoise_kernel : int
        Median blur kernel size for denoising
    condition_label : str
        Label for this experimental condition
    use_full_frame : bool
        Whether to use full frame or allow manual ROI
    manual_roi : tuple
        (x, y, w, h) to restrict centroid tracking to specific region
    exclude_outer_ring : bool
        Whether to exclude outer ring/edge regions from tracking
    edge_exclusion_radius : int or None
        Pixels from edge to exclude (if None, auto-calculated as 15% of radius)
    show_threshold_mask : bool
        Whether to show visualization of thresholded mask
    use_adaptive_threshold : bool
        If True, uses adaptive thresholding (better for non-uniform brightness)
        If False, uses global percentile threshold
    adaptive_block_size : int
        Block size for adaptive threshold (must be odd number, larger = smoother)
        Typical values: 31, 51, 71
    
    Returns:
    --------
    Dictionary with tracking results
    """
    
    # Setup
    ph = Phantom()
    
    try:
        file_path = ph.file_select_dialog()
    except:
        file_path = None
    
    if not file_path:
        print("\n[INFO] Please enter the full path to your .cine file:")
        file_path = input("File path: ").strip().strip('"').strip("'")
        
        if not file_path or not os.path.exists(file_path):
            print("[ERROR] No valid file provided.")
            ph.close()
            return None
    
    print(f"[INFO] Loading file: {file_path}")
    
    save_dir = get_experiment_folder()
    our_cine = cine.Cine.from_filepath(file_path)

    try:
        start, end = our_cine.recorded_range
    except Exception:
        start, end = our_cine.range
    
    print(f"[INFO] Video range: {start} to {end}")
    start = max(start + skip_initial_frames, start)
    
    # Filter dark frames
    frame_numbers_valid, intensity_trace = filter_dark_frames(our_cine, start, end, dark_threshold)
    
    if len(frame_numbers_valid) == 0:
        print("[ERROR] No valid frames found above threshold!")
        ph.close()
        return None
    
    # Detect ramp if requested
    if detect_ramp and len(intensity_trace) > block_size * 2:
        print("[INFO] Analyzing intensity trace for laser ramp-up...")
        block_means = []
        for i in range(0, len(intensity_trace) - block_size + 1, block_size):
            block = intensity_trace[i:i+block_size]
            block_means.append(np.mean(block))
        
        block_means = np.array(block_means)
        ramp_start, ramp_end = find_ramp_blocks(block_means)
        
        if ramp_start is not None:
            ramp_start_frame = frame_numbers_valid[ramp_start * block_size]
            print(f"[INFO] Detected laser ramp at frame {ramp_start_frame}")
            
            valid_indices = [i for i, f in enumerate(frame_numbers_valid) if f >= ramp_start_frame]
            frame_numbers_valid = [frame_numbers_valid[i] for i in valid_indices]
            intensity_trace = [intensity_trace[i] for i in valid_indices]
    
    # Get first frame for visualization
    first_valid_frame_num = frame_numbers_valid[0]
    first_frame = np.squeeze(our_cine.get_images(utils.FrameRange(first_valid_frame_num, first_valid_frame_num)))
    
    if first_frame.ndim > 2:
        first_frame = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
    
    # Define ROI
    if manual_roi is not None:
        x, y, w, h = manual_roi
        print(f"[INFO] Using manual ROI: {w}x{h} pixels at ({x}, {y})")
    elif use_full_frame:
        x, y, w, h = 0, 0, first_frame.shape[1], first_frame.shape[0]
        print(f"[INFO] Using full frame: {w}x{h} pixels")
    
    roi_center = (w // 2, h // 2)
    
    # ========== VISUALIZE THRESHOLD MASK ==========
    if show_threshold_mask:
        print("\n[INFO] Creating threshold mask visualization...")
        
        # Get ROI from first frame
        roi_first = first_frame[y:y+h, x:x+w]
        frame_denoised = cv2.medianBlur(roi_first, 3)
        
        # Create exclusion mask
        if exclude_outer_ring:
            h_roi, w_roi = roi_first.shape
            mask_exclude = np.ones_like(roi_first, dtype=bool)
            
            edge_rad = edge_exclusion_radius if edge_exclusion_radius is not None else int(min(w_roi, h_roi) * 0.15)
            
            Y, X = np.ogrid[:h_roi, :w_roi]
            dist_from_center = np.sqrt((X - roi_center[0])**2 + (Y - roi_center[1])**2)
            max_radius = min(roi_center[0], roi_center[1], 
                            w_roi - roi_center[0], h_roi - roi_center[1])
            inner_radius = max_radius - edge_rad
            
            mask_exclude = dist_from_center < inner_radius
            frame_masked = frame_denoised.copy()
            frame_masked[~mask_exclude] = 0
            
            print(f"[INFO] Excluding outer {edge_rad} pixels from edge (inner radius: {inner_radius:.1f})")
        else:
            frame_masked = frame_denoised
            mask_exclude = np.ones_like(roi_first, dtype=bool)
        
        # Apply threshold
        threshold_val = np.percentile(frame_masked[frame_masked > 0], threshold_percentile)
        threshold_mask = frame_masked > threshold_val
        
        method_text = f"Global Threshold (>{threshold_percentile}th percentile)"
        
        if use_adaptive_threshold:
            # Also show adaptive threshold result
            frame_8bit = cv2.normalize(frame_masked, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            adaptive_mask = cv2.adaptiveThreshold(
                frame_8bit, 
                255, 
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 
                adaptive_block_size,
                -10
            )
            threshold_mask = (adaptive_mask > 0) & mask_exclude
            method_text = f"Adaptive Threshold (block={adaptive_block_size})"
        
        print(f"[INFO] Threshold method: {method_text}")
        print(f"[INFO] Pixels above threshold: {np.sum(threshold_mask)}")
        
        # Create visualization
        fig_mask, axes_mask = plt.subplots(1, 4, figsize=(20, 5))
        
        # Original ROI
        axes_mask[0].imshow(roi_first, cmap='gray')
        axes_mask[0].set_title('Original ROI', fontsize=12, fontweight='bold')
        axes_mask[0].axis('off')
        
        # Exclusion mask
        axes_mask[1].imshow(mask_exclude, cmap='RdYlGn')
        if exclude_outer_ring:
            circle = plt.Circle(roi_center, inner_radius, color='yellow', fill=False, linewidth=2)
            axes_mask[1].add_patch(circle)
        axes_mask[1].set_title('Edge Exclusion Mask\n(Green=Included, Red=Excluded)', fontsize=12, fontweight='bold')
        axes_mask[1].axis('off')
        
        # Masked frame
        axes_mask[2].imshow(frame_masked, cmap='gray')
        axes_mask[2].set_title('After Edge Exclusion', fontsize=12, fontweight='bold')
        axes_mask[2].axis('off')
        
        # Threshold result
        axes_mask[3].imshow(threshold_mask, cmap='hot')
        if np.any(threshold_mask):
            cy_mask, cx_mask = center_of_mass(threshold_mask)
            axes_mask[3].plot(cx_mask, cy_mask, 'g+', markersize=20, markeredgewidth=3)
            axes_mask[3].plot(cx_mask, cy_mask, 'go', markersize=10, fillstyle='none', markeredgewidth=2)
        axes_mask[3].set_title(f'Threshold Result\n{method_text}\nGreen = Centroid', 
                               fontsize=12, fontweight='bold')
        axes_mask[3].axis('off')
        
        plt.suptitle(f'{condition_label}\nThreshold Mask Visualization - Verify tracking region is correct!', 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, "threshold_mask_visualization.png"), dpi=300, bbox_inches='tight')
        plt.show()
        print(f"[INFO] Threshold mask visualization saved")
    
    # Track centroid across all frames
    print(f"\n[INFO] Tracking centroid across {len(frame_numbers_valid)} frames...")
    
    centroid_x = []
    centroid_y = []
    frame_indices = []
    
    for idx, frame_num in enumerate(frame_numbers_valid):
        if idx % 100 == 0:
            print(f"[INFO] Processing frame {idx+1}/{len(frame_numbers_valid)}")
        
        frame = np.squeeze(our_cine.get_images(utils.FrameRange(frame_num, frame_num)))
        
        if frame.ndim > 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Extract ROI
        roi = frame[y:y+h, x:x+w]
        
        # Compute centroid in ROI coordinates with edge exclusion
        cx, cy = compute_centroid(roi, 
                                  threshold_percentile=threshold_percentile,
                                  exclude_edges=exclude_outer_ring,
                                  edge_exclusion_radius=edge_exclusion_radius,
                                  frame_center=roi_center,
                                  use_adaptive_threshold=use_adaptive_threshold,
                                  adaptive_block_size=adaptive_block_size)
        
        # Convert to full frame coordinates
        cx_full = cx + x
        cy_full = cy + y
        
        centroid_x.append(cx_full)
        centroid_y.append(cy_full)
        frame_indices.append(idx)
    
    centroid_x = np.array(centroid_x)
    centroid_y = np.array(centroid_y)
    frame_indices = np.array(frame_indices)
    
    # Calculate displacement from starting position
    displacement_x = centroid_x - centroid_x[0]
    displacement_y = centroid_y - centroid_y[0]
    displacement_magnitude = np.sqrt(displacement_x**2 + displacement_y**2)
    
    # Calculate statistics
    mean_x = np.mean(centroid_x)
    mean_y = np.mean(centroid_y)
    std_x = np.std(centroid_x)
    std_y = np.std(centroid_y)
    max_displacement = np.max(displacement_magnitude)
    mean_displacement = np.mean(displacement_magnitude)
    
    print("\n" + "="*60)
    print("CENTROID TRACKING RESULTS")
    print("="*60)
    print(f"Total frames tracked: {len(centroid_x)}")
    print(f"Mean position: ({mean_x:.2f}, {mean_y:.2f})")
    print(f"Std deviation: ({std_x:.2f}, {std_y:.2f}) pixels")
    print(f"Max displacement: {max_displacement:.2f} pixels")
    print(f"Mean displacement: {mean_displacement:.2f} pixels")
    print("="*60)
    
    # ========== VISUALIZE FIRST FRAME WITH INITIAL CENTROID ==========
    print("\n[INFO] Creating ROI visualization...")
    
    vis_frame = cv2.normalize(first_frame, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    vis_frame_color = cv2.cvtColor(vis_frame, cv2.COLOR_GRAY2BGR)
    
    # Draw ROI boundary
    cv2.rectangle(vis_frame_color, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    # Draw initial centroid position
    initial_cx, initial_cy = int(centroid_x[0]), int(centroid_y[0])
    cv2.circle(vis_frame_color, (initial_cx, initial_cy), 5, (0, 0, 255), -1)
    cv2.circle(vis_frame_color, (initial_cx, initial_cy), 10, (0, 0, 255), 2)
    
    # Draw mean position
    mean_cx, mean_cy = int(mean_x), int(mean_y)
    cv2.circle(vis_frame_color, (mean_cx, mean_cy), 5, (255, 0, 0), -1)
    cv2.circle(vis_frame_color, (mean_cx, mean_cy), 10, (255, 0, 0), 2)
    
    plt.figure(figsize=(12, 10))
    plt.imshow(vis_frame_color)
    plt.title(f'ROI and Initial Centroid Position - {condition_label}\n'
              f'Green: ROI | Red: Initial Position | Blue: Mean Position', 
              fontsize=12, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "ROI_and_centroid_visualization.png"), dpi=300, bbox_inches='tight')
    plt.show()
    print(f"[INFO] ROI visualization saved")
    
    # ========== PLOT CENTROID TRAJECTORY ==========
    print("\n[INFO] Creating trajectory visualization...")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    
    # Plot 1: X and Y positions over time
    ax1 = axes[0, 0]
    ax1.plot(frame_indices, centroid_x, 'b-', linewidth=1, alpha=0.7, label='X position')
    ax1.axhline(mean_x, color='b', linestyle='--', linewidth=2, label=f'Mean X = {mean_x:.2f}')
    ax1.fill_between(frame_indices, mean_x - std_x, mean_x + std_x, color='b', alpha=0.2)
    ax1.set_xlabel('Frame Index', fontsize=12)
    ax1.set_ylabel('X Position (pixels)', fontsize=12)
    ax1.set_title('Centroid X Position Over Time', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2 = axes[0, 1]
    ax2.plot(frame_indices, centroid_y, 'r-', linewidth=1, alpha=0.7, label='Y position')
    ax2.axhline(mean_y, color='r', linestyle='--', linewidth=2, label=f'Mean Y = {mean_y:.2f}')
    ax2.fill_between(frame_indices, mean_y - std_y, mean_y + std_y, color='r', alpha=0.2)
    ax2.set_xlabel('Frame Index', fontsize=12)
    ax2.set_ylabel('Y Position (pixels)', fontsize=12)
    ax2.set_title('Centroid Y Position Over Time', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 2: 2D trajectory
    ax3 = axes[1, 0]
    scatter = ax3.scatter(centroid_x, centroid_y, c=frame_indices, cmap='viridis', 
                         s=10, alpha=0.6)
    ax3.plot(centroid_x, centroid_y, 'gray', linewidth=0.5, alpha=0.3)
    ax3.plot(centroid_x[0], centroid_y[0], 'go', markersize=12, label='Start', markeredgecolor='black', markeredgewidth=2)
    ax3.plot(centroid_x[-1], centroid_y[-1], 'ro', markersize=12, label='End', markeredgecolor='black', markeredgewidth=2)
    ax3.plot(mean_x, mean_y, 'b*', markersize=15, label='Mean', markeredgecolor='black', markeredgewidth=1.5)
    ax3.set_xlabel('X Position (pixels)', fontsize=12)
    ax3.set_ylabel('Y Position (pixels)', fontsize=12)
    ax3.set_title('2D Centroid Trajectory', fontsize=14, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_aspect('equal')
    plt.colorbar(scatter, ax=ax3, label='Frame Index')
    
    # Plot 3: Displacement magnitude
    ax4 = axes[1, 1]
    ax4.plot(frame_indices, displacement_magnitude, 'g-', linewidth=1, alpha=0.7)
    ax4.axhline(mean_displacement, color='orange', linestyle='--', linewidth=2, 
                label=f'Mean = {mean_displacement:.2f}px')
    ax4.set_xlabel('Frame Index', fontsize=12)
    ax4.set_ylabel('Displacement (pixels)', fontsize=12)
    ax4.set_title('Displacement from Initial Position', fontsize=14, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.suptitle(f'{condition_label}\nCentroid Tracking Analysis', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, f"centroid_tracking_{condition_label.replace(' ', '_')}.png"), 
                dpi=300, bbox_inches='tight')
    plt.show()
    
    # ========== CREATE VIDEO WITH CENTROID OVERLAY ==========
    print("\n[INFO] Creating video with centroid tracking overlay...")
    print(f"[INFO] Processing ALL {len(frame_numbers_valid)} frames...")
    print("[INFO] This may take several minutes for long videos...")
    
    # Use ALL frames (no sampling)
    sampled_indices = range(0, len(frame_numbers_valid))
    
    # Create video writer
    video_filename = os.path.join(save_dir, f"centroid_tracking_video_{condition_label.replace(' ', '_')}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 30
    frame_width, frame_height = first_frame.shape[1], first_frame.shape[0]
    
    # Add space for trajectory trail (side-by-side view)
    canvas_width = frame_width * 2
    out = cv2.VideoWriter(video_filename, fourcc, fps, (canvas_width, frame_height))
    
    # Store historical centroids for trail
    trail_length = 50  # Number of past positions to show
    
    for idx_count, idx in enumerate(sampled_indices):
        if idx_count % 100 == 0:
            print(f"[INFO] Processing video frame {idx_count+1}/{len(sampled_indices)}")
        
        frame_num = frame_numbers_valid[idx]
        frame = np.squeeze(our_cine.get_images(utils.FrameRange(frame_num, frame_num)))
        
        if frame.ndim > 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Convert to color for overlay
        frame_color = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        
        # Draw current centroid
        cx_current = int(centroid_x[idx])
        cy_current = int(centroid_y[idx])
        cv2.circle(frame_color, (cx_current, cy_current), 8, (0, 255, 0), -1)  # Green dot
        cv2.circle(frame_color, (cx_current, cy_current), 15, (0, 255, 0), 2)  # Green ring
        
        # Draw trail of past positions
        start_trail = max(0, idx - trail_length)
        for trail_idx in range(start_trail, idx):
            alpha = (trail_idx - start_trail) / trail_length  # Fade effect
            color = (0, int(255 * alpha), int(255 * (1 - alpha)))  # Green to red gradient
            cx_trail = int(centroid_x[trail_idx])
            cy_trail = int(centroid_y[trail_idx])
            cv2.circle(frame_color, (cx_trail, cy_trail), 3, color, -1)
        
        # Draw initial position reference
        cx_initial = int(centroid_x[0])
        cy_initial = int(centroid_y[0])
        cv2.circle(frame_color, (cx_initial, cy_initial), 5, (255, 0, 0), -1)  # Blue dot
        cv2.circle(frame_color, (cx_initial, cy_initial), 10, (255, 0, 0), 2)
        
        # Add text overlay with info
        cv2.putText(frame_color, f"Frame: {idx}/{len(frame_numbers_valid)-1}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame_color, f"Position: ({cx_current}, {cy_current})", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame_color, f"Displacement: {displacement_magnitude[idx]:.2f} px", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Create trajectory plot on right side
        trajectory_canvas = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
        
        # Scale trajectory to fit canvas with margins
        margin = 50
        x_min, x_max = np.min(centroid_x), np.max(centroid_x)
        y_min, y_max = np.min(centroid_y), np.max(centroid_y)
        
        # Add padding to avoid edge clipping
        x_range = max(x_max - x_min, 1)
        y_range = max(y_max - y_min, 1)
        x_min -= x_range * 0.1
        x_max += x_range * 0.1
        y_min -= y_range * 0.1
        y_max += y_range * 0.1
        
        def scale_to_canvas(x, y):
            scaled_x = int(margin + (x - x_min) / (x_max - x_min) * (frame_width - 2*margin))
            scaled_y = int(margin + (y - y_min) / (y_max - y_min) * (frame_height - 2*margin))
            return (scaled_x, scaled_y)
        
        # Draw all trajectory up to current frame
        for traj_idx in range(max(0, idx - 200), idx):  # Show last 200 points
            pt1 = scale_to_canvas(centroid_x[traj_idx], centroid_y[traj_idx])
            pt2 = scale_to_canvas(centroid_x[traj_idx + 1], centroid_y[traj_idx + 1])
            alpha = (traj_idx - max(0, idx - 200)) / 200
            color = (int(100 * alpha), int(200 * alpha), int(255 * alpha))
            cv2.line(trajectory_canvas, pt1, pt2, color, 2)
        
        # Draw start and current positions on trajectory plot
        start_pt = scale_to_canvas(centroid_x[0], centroid_y[0])
        current_pt = scale_to_canvas(centroid_x[idx], centroid_y[idx])
        cv2.circle(trajectory_canvas, start_pt, 8, (255, 0, 0), -1)  # Blue start
        cv2.circle(trajectory_canvas, current_pt, 8, (0, 255, 0), -1)  # Green current
        
        # Add title to trajectory canvas
        cv2.putText(trajectory_canvas, "Trajectory", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Combine both views side by side
        combined = np.hstack([frame_color, trajectory_canvas])
        
        out.write(combined)
    
    out.release()
    print(f"[INFO] Video saved to: {video_filename}")
    
    # ========== PLOT DISPLACEMENT COMPONENTS ==========
    print("\n[INFO] Creating displacement component plots...")
    
    fig2, axes2 = plt.subplots(1, 2, figsize=(16, 6))
    
    ax1 = axes2[0]
    ax1.plot(frame_indices, displacement_x, 'b-', linewidth=1, alpha=0.7)
    ax1.axhline(0, color='black', linestyle='-', linewidth=1)
    ax1.set_xlabel('Frame Index', fontsize=12)
    ax1.set_ylabel('X Displacement (pixels)', fontsize=12)
    ax1.set_title('X-Direction Displacement', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    ax2 = axes2[1]
    ax2.plot(frame_indices, displacement_y, 'r-', linewidth=1, alpha=0.7)
    ax2.axhline(0, color='black', linestyle='-', linewidth=1)
    ax2.set_xlabel('Frame Index', fontsize=12)
    ax2.set_ylabel('Y Displacement (pixels)', fontsize=12)
    ax2.set_title('Y-Direction Displacement', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle(f'{condition_label}\nDisplacement Components', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, f"displacement_components_{condition_label.replace(' ', '_')}.png"), 
                dpi=300, bbox_inches='tight')
    plt.show()
    
    # ========== SAVE RESULTS ==========
    results = {
        'condition': condition_label,
        'total_frames': len(frame_indices),
        'statistics': {
            'mean_x': float(mean_x),
            'mean_y': float(mean_y),
            'std_x': float(std_x),
            'std_y': float(std_y),
            'max_displacement': float(max_displacement),
            'mean_displacement': float(mean_displacement)
        },
        'initial_position': {
            'x': float(centroid_x[0]),
            'y': float(centroid_y[0])
        },
        'final_position': {
            'x': float(centroid_x[-1]),
            'y': float(centroid_y[-1])
        },
        'roi': {
            'x': x,
            'y': y,
            'width': w,
            'height': h
        }
    }
    
    results_file = os.path.join(save_dir, f"centroid_tracking_results_{condition_label.replace(' ', '_')}.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save full trajectory data as CSV
    trajectory_file = os.path.join(save_dir, f"centroid_trajectory_data_{condition_label.replace(' ', '_')}.csv")
    with open(trajectory_file, 'w') as f:
        f.write("frame_index,actual_frame_number,centroid_x,centroid_y,displacement_x,displacement_y,displacement_magnitude\n")
        for i in range(len(frame_indices)):
            f.write(f"{frame_indices[i]},{frame_numbers_valid[i]},{centroid_x[i]},{centroid_y[i]},"
                   f"{displacement_x[i]},{displacement_y[i]},{displacement_magnitude[i]}\n")
    
    print(f"\n[INFO] Results saved to: {results_file}")
    print(f"[INFO] Trajectory data saved to: {trajectory_file}")
    print(f"[INFO] Plots saved to: {save_dir}/")
    
    ph.close()
    
    return results


# Run the analysis
if __name__ == "__main__":
    results = track_centroid_across_frames(
        skip_initial_frames=300,
        dark_threshold=3000,
        detect_ramp=True,
        block_size=30,
        threshold_percentile=60,  # Only used if use_adaptive_threshold=False
        denoise_kernel=3,
        condition_label="Position X_4 - Rolling Thrust Halloweeen Data",  # Change this for each run
        use_full_frame=False,  # Set to False and provide manual_roi if needed
        manual_roi=(120, 110, 350, 350),  # e.g., (100, 100, 400, 400) for specific region
        exclude_outer_ring=True,  # Exclude bright outer ring
        edge_exclusion_radius=None,  # Auto-calculate (or set pixels, e.g., 50)
        show_threshold_mask=True,  # Show what algorithm "sees"
        use_adaptive_threshold=False,  # NEW: Try adaptive thresholding!
        adaptive_block_size=31  # NEW: Block size (must be odd: 31, 51, 71, etc.)
    )
    
    print("\n" + "="*60)
    print("CENTROID TRACKING COMPLETE")
    print("="*60)
    print("\nYou now have:")
    print("- threshold_mask_visualization.png - Shows what the algorithm 'sees' for tracking")
    print("- ROI_and_centroid_visualization.png - Shows ROI and initial centroid")
    print("- centroid_tracking_[condition].png - 4-panel tracking visualization")
    print("- displacement_components_[condition].png - X and Y displacement plots")
    print("- centroid_tracking_video_[condition].mp4 - VIDEO showing tracking in real-time!")
    print("- centroid_tracking_results_[condition].json - Summary statistics")
    print("- centroid_trajectory_data_[condition].csv - Full frame-by-frame data")
    print("\n** Check threshold_mask_visualization.png FIRST to verify tracking region! **")
    print("** Then watch the video to verify tracking accuracy! **")
    print("="*60)
