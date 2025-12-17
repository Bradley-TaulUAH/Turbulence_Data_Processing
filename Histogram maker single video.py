import numpy as np
import matplotlib.pyplot as plt
import os
from tkinter import filedialog, Tk, simpledialog, messagebox


def bootstrap_si_distribution(intensity_trace, n_bootstrap=10000, block_size=100):
    """Generate SI distribution via bootstrap resampling."""
    n_samples = len(intensity_trace)
    n_blocks = max(1, n_samples // block_size)
    si_samples = []
    
    for _ in range(n_bootstrap):
        block_indices = np.random.choice(n_blocks, size=n_blocks, replace=True)
        resampled = []
        for idx in block_indices:
            start = idx * block_size
            end = min(start + block_size, n_samples)
            resampled.append(intensity_trace[start:end])
        
        resampled = np.concatenate(resampled)
        mean_i = np.mean(resampled)
        var_i = np.var(resampled)
        si = var_i / (mean_i ** 2 + 1e-6)
        si_samples.append(si)
    
    return np.array(si_samples)


def load_intensity_trace(csv_path):
    """Load tracking aperture intensity from CSV file."""
    data = np.genfromtxt(csv_path, delimiter=',', skip_header=1)
    tracking_intensity = data[:, 2]
    return tracking_intensity


def create_multi_position_histogram(all_positions_data, n_bootstrap=10000, save_path=None):
    """Create histogram with multiple positions in one figure (2x2 grid)."""
    
    n_positions = len(all_positions_data)
    
    # Create 2x2 grid
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))
    axes = axes.flatten()
    
    all_stats = {}
    
    for idx, position_data in enumerate(all_positions_data):
        ax = axes[idx]
        position_label = position_data['label']
        distance_label = position_data['distance']
        si_control = position_data['si_control']
        si_rolling = position_data['si_rolling']
        
        # Combine all data to determine bin range
        all_si = np.concatenate([si_control, si_rolling])
        bins = np.linspace(all_si.min(), all_si.max(), 60)
        
        # Plot overlapping histograms
        ax.hist(si_control, bins=bins, alpha=0.7, color='gray', edgecolor='black',
                linewidth=1.5, label='Control (Background)', density=True)
        ax.hist(si_rolling, bins=bins, alpha=0.7, color='purple', edgecolor='darkviolet',
                linewidth=1.5, label='Rolling Thrust', density=True)
        
        # Calculate means
        mean_control = np.mean(si_control)
        mean_rolling = np.mean(si_rolling)
        
        # Add vertical dashed lines for means
        ax.axvline(mean_control, color='black', linestyle='--', linewidth=2.5, alpha=0.9)
        ax.axvline(mean_rolling, color='darkviolet', linestyle='--', linewidth=2.5, alpha=0.9)
        
        # Labels and title
        ax.set_xlabel('Scintillation Index (SI)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Probability Density', fontsize=12, fontweight='bold')
        
        title = position_label
        if distance_label:
            title += f' ({distance_label})'
        ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
        
        # Calculate percent increase
        percent_increase = ((mean_rolling - mean_control) / mean_control) * 100
        
        # Add text box with statistics
        textstr = (f'Control: {mean_control:.6f}\n'
                   f'Rolling: {mean_rolling:.6f}\n'
                   f'Increase: {percent_increase:+.1f}%')
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.98, 0.97, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', horizontalalignment='right', bbox=props,
                fontweight='bold')
        
        ax.legend(fontsize=10, loc='upper left')
        ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
        
        # Store statistics
        all_stats[position_label] = {
            'control': {
                'mean': mean_control,
                'std': np.std(si_control),
                'ci_low': np.percentile(si_control, 2.5),
                'ci_high': np.percentile(si_control, 97.5)
            },
            'rolling': {
                'mean': mean_rolling,
                'std': np.std(si_rolling),
                'ci_low': np.percentile(si_rolling, 2.5),
                'ci_high': np.percentile(si_rolling, 97.5)
            },
            'percent_increase': percent_increase
        }
    
    # Hide unused subplots
    for idx in range(n_positions, 4):
        axes[idx].set_visible(False)
    
    plt.suptitle('Impact of Rolling Thrust on Scintillation Index at Different Positions\n(Tracking Aperture Method - Bootstrap Distribution)',
                 fontsize=14, fontweight='bold', y=0.995)
    
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\n[INFO] Figure saved to: {save_path}")
    
    plt.show()
    
    return all_stats


def print_statistics(all_stats):
    """Print statistical comparison for all positions."""
    print("\n" + "=" * 90)
    print("SCINTILLATION INDEX STATISTICS - TRACKING APERTURE METHOD")
    print("=" * 90)
    print(f"{'Position':<15} {'Condition':<12} {'Mean SI':<12} {'Std Dev':<12} {'95% CI':<25}")
    print("-" * 90)
    
    for position_label, stats in all_stats.items():
        # Control
        print(f"{position_label:<15} {'Control':<12} {stats['control']['mean']:<12.6f} "
              f"{stats['control']['std']:<12.6f} "
              f"[{stats['control']['ci_low']:.6f}, {stats['control']['ci_high']:.6f}]")
        
        # Rolling thrust
        print(f"{'':<15} {'Rolling':<12} {stats['rolling']['mean']:<12.6f} "
              f"{stats['rolling']['std']:<12.6f} "
              f"[{stats['rolling']['ci_low']:.6f}, {stats['rolling']['ci_high']:.6f}]")
        
        print(f"{'':<15} {'Increase':<12} {stats['percent_increase']:+.2f}%")
        print("-" * 90)
    
    print("=" * 90)


if __name__ == "__main__":
    # Create Tkinter root window (hidden)
    root = Tk()
    root.withdraw()
    
    print("\n" + "=" * 70)
    print("MULTI-POSITION SCINTILLATION INDEX COMPARISON")
    print("=" * 70)
    
    # Ask how many positions
    n_positions = simpledialog.askinteger(
        "Number of Positions",
        "How many positions do you want to compare? (1-4)",
        initialvalue=4,
        minvalue=1,
        maxvalue=4
    )
    
    if n_positions is None:
        print("[ERROR] No number of positions specified.")
        exit(1)
    
    # Ask for bootstrap iterations
    n_bootstrap = simpledialog.askinteger(
        "Bootstrap Iterations",
        "Enter number of bootstrap iterations:",
        initialvalue=10000,
        minvalue=1000,
        maxvalue=50000
    )
    
    if n_bootstrap is None:
        n_bootstrap = 10000
    
    all_positions_data = []
    
    # Loop through positions
    for i in range(n_positions):
        print(f"\n{'='*70}")
        print(f"POSITION {i+1} of {n_positions}")
        print(f"{'='*70}")
        
        # Get position label and distance
        position_label = simpledialog.askstring(
            f"Position {i+1} Label",
            f"Enter label for position {i+1} (e.g., 'Position 1', 'Position X3'):",
            initialvalue=f"Position {i+1}"
        )
        
        distance_label = simpledialog.askstring(
            f"Position {i+1} Distance",
            f"Enter distance for position {i+1} (e.g., '134m', '89m') or leave blank:",
            initialvalue=""
        )
        
        # Select control/background file
        messagebox.showinfo("File Selection", f"Select CONTROL file for {position_label}")
        control_path = filedialog.askopenfilename(
            title=f"{position_label} - Select CONTROL file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not control_path:
            print(f"[WARNING] No control file selected for {position_label}, skipping.")
            continue
        
        print(f"[INFO] Control: {os.path.basename(control_path)}")
        
        # Select rolling thrust file
        messagebox.showinfo("File Selection", f"Select ROLLING THRUST file for {position_label}")
        rolling_path = filedialog.askopenfilename(
            title=f"{position_label} - Select ROLLING THRUST file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not rolling_path:
            print(f"[WARNING] No rolling thrust file selected for {position_label}, skipping.")
            continue
        
        print(f"[INFO] Rolling Thrust: {os.path.basename(rolling_path)}")
        
        # Load intensity traces
        print(f"[INFO] Loading data for {position_label}...")
        intensity_control = load_intensity_trace(control_path)
        intensity_rolling = load_intensity_trace(rolling_path)
        
        print(f"[INFO] Control frames: {len(intensity_control)}")
        print(f"[INFO] Rolling thrust frames: {len(intensity_rolling)}")
        
        # Compute bootstrap distributions
        print(f"[INFO] Computing bootstrap distributions...")
        si_control = bootstrap_si_distribution(intensity_control, n_bootstrap=n_bootstrap)
        si_rolling = bootstrap_si_distribution(intensity_rolling, n_bootstrap=n_bootstrap)
        
        # Store data
        all_positions_data.append({
            'label': position_label,
            'distance': distance_label,
            'si_control': si_control,
            'si_rolling': si_rolling
        })
    
    root.destroy()
    
    if len(all_positions_data) == 0:
        print("[ERROR] No valid position data collected.")
        exit(1)
    
    # Create output path
    save_dir = os.path.dirname(control_path)
    if not save_dir:
        save_dir = "."
    save_path = os.path.join(save_dir, "si_histogram_all_positions.png")
    
    # Create multi-position histogram
    print(f"\n[INFO] Creating combined histogram...")
    all_stats = create_multi_position_histogram(all_positions_data, n_bootstrap, save_path)
    
    # Print statistics
    print_statistics(all_stats)
    
    print("\n[INFO] Analysis complete!")
