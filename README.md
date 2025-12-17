# Turbulence Data Processing Toolkit

A Python toolkit for processing high-speed camera data to analyze atmospheric turbulence effects on laser beam propagation. This toolkit specializes in tracking laser spot centroids and calculating scintillation index (SI) using the tracking aperture method.

## 📖 Overview

This toolkit processes `.cine` video files from Phantom high-speed cameras to:

1. **Track centroid positions** of laser spots across thousands of frames
2. **Calculate scintillation index** using both fixed and tracking aperture methods
3. **Compare experimental conditions** with publication-ready visualizations
4. **Remove geometric wander effects** to isolate true atmospheric turbulence

The tracking aperture method separates beam motion (geometric wander) from atmospheric scintillation, providing more accurate measurements of turbulence-induced intensity fluctuations.

## ✨ Features

- **Automated Centroid Tracking**
  - Adaptive threshold detection for varying illumination
  - ROI (Region of Interest) support for focused tracking
  - Laser ramp-up detection and dark frame filtering
  - Real-time visualization with tracking videos

- **Scintillation Index Calculation**
  - Fixed aperture method (traditional approach)
  - Tracking aperture method (removes geometric wander)
  - Bootstrap statistical analysis with confidence intervals
  - Comparative analysis between methods

- **Publication-Ready Outputs**
  - High-resolution (300 DPI) plots and histograms
  - Comprehensive CSV data exports
  - JSON metadata for reproducibility
  - Video visualizations of tracking results

- **Robust Processing**
  - Handles large video files (1-10 GB `.cine` files)
  - Progress tracking for long-running operations
  - Parameter tuning for different experimental setups
  - Quality control visualizations

## 🚀 Quick Start

### Prerequisites

- **Windows 10/11** (required for Phantom SDK)
- **Anaconda/Miniconda**
- **Phantom SDK** (from Vision Research)
- **~5 GB disk space** for dependencies

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Bradley-TaulUAH/Turbulence_Data_Processing.git
   cd Turbulence_Data_Processing
   ```

2. **Set up the environment:**
   
   Follow the detailed instructions in [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md):
   - Install Anaconda
   - Install Phantom SDK and add to PATH
   - Create conda environment: `conda create -n turbulence python=3.9`
   - Install dependencies: `pip install -r requirements.txt`
   - Install pyphantom: `pip install pyphantom`

3. **Verify installation:**
   ```bash
   conda activate turbulence
   python -c "from pyphantom import Phantom; print('Setup complete!')"
   ```

### Usage

See [QUICKSTART.md](QUICKSTART.md) for a complete tutorial. Basic workflow:

1. **Track centroid** in your `.cine` video:
   ```bash
   python "Centroid tracker updated.py"
   ```
   - Select your video file
   - Adjust parameters for your setup
   - Review tracking visualization

2. **Calculate scintillation index**:
   ```bash
   python "Combined centroid and intensity.py"
   ```
   - Select the centroid CSV from step 1
   - Select the corresponding video file
   - Choose aperture radius (default: 30 pixels)

3. **Generate comparison histograms**:
   ```bash
   python "Histogram maker single video.py"
   ```
   - Compare multiple experimental conditions
   - Get statistical analysis with confidence intervals
   - Create publication-ready figures

## 📊 Example Results

**Typical Scintillation Index Values:**

| Condition | SI Range | Description |
|-----------|----------|-------------|
| Weak turbulence | 0.001 - 0.01 | Clear air, minimal disturbance |
| Moderate turbulence | 0.01 - 0.05 | Natural atmospheric effects |
| Strong turbulence | 0.05 - 0.2 | Heat plumes, jet exhaust |
| Very strong | > 0.2 | Near-field turbulence, saturation |

**Key Findings:**
- Tracking aperture method typically reduces SI by 20-50% compared to fixed aperture
- Geometric wander can contribute 30-80% of measured SI in fixed aperture measurements
- Thrust/turbulence sources typically increase SI by 50-200%

## 📂 Data Repository

This repository includes a `data/` directory for storing experimental results:

- **raw_data/** - Centroid tracking CSV outputs
- **processed_data/** - Scintillation index calculation results  
- **example_data/** - Sample datasets for testing

**See [DATA_GUIDE.md](DATA_GUIDE.md)** for complete instructions on how to add your experimental data files to the repository. You can add CSV files directly without zipping them.

## 📁 Repository Structure

```
Turbulence_Data_Processing/
├── README.md                           # This file
├── QUICKSTART.md                       # Detailed tutorial
├── ENVIRONMENT_SETUP.md                # Installation guide
├── DATA_GUIDE.md                       # Guide for adding experimental data
├── requirements.txt                    # Python dependencies
├── Centroid tracker updated.py         # Step 1: Track laser spot
├── Combined centroid and intensity.py  # Step 2: Calculate SI
├── Histogram maker single video.py     # Step 3: Compare conditions
└── data/                               # Experimental data directory
    ├── README.md                       # Data organization guide
    ├── raw_data/                       # Raw centroid CSV files
    ├── processed_data/                 # Processed SI results
    └── example_data/                   # Example datasets
```

## 🔬 Scientific Background

### Scintillation Index

The scintillation index (SI) quantifies intensity fluctuations in optical beams propagating through turbulent media:

```
SI = σ²_I / ⟨I⟩²
```

where `σ²_I` is the intensity variance and `⟨I⟩` is the mean intensity.

### Tracking Aperture Method

Traditional fixed aperture measurements include both:
1. **Atmospheric scintillation** - True turbulence effect
2. **Geometric wander** - Beam motion artifacts

The tracking aperture method follows the beam centroid, measuring only atmospheric scintillation. This is critical for accurate turbulence characterization, especially in strong turbulence or when beam steering is significant.

## 🛠️ Requirements

### Software
- Python 3.9+
- Anaconda/Miniconda
- Phantom Camera Control (PCC) 4.5+ with SDK
- Visual Studio Code (recommended)

### Python Packages
- numpy >= 1.26.4
- opencv-python >= 4.10.0
- matplotlib >= 3.10.0
- scipy >= 1.14.1
- pandas >= 2.2.3
- pyphantom >= 1.0.0
- tkinter (usually included with Python)

See `requirements.txt` for complete list.

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Step-by-step tutorial for processing your first dataset
- **[ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)** - Detailed installation and configuration guide

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add YourFeature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

## 📄 License

This project is available for academic and research use. Please cite this repository if you use it in your research.

## 👥 Authors

Bradley Taul - University of Alabama in Huntsville

## 🐛 Issues and Support

If you encounter any problems or have questions:

1. Check [QUICKSTART.md](QUICKSTART.md) and [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)
2. Review the troubleshooting sections in the documentation
3. Open an issue on GitHub with:
   - Your operating system and version
   - Output of `conda list`
   - Full error message
   - Steps to reproduce

## 🙏 Acknowledgments

- Vision Research for the Phantom SDK
- The pyphantom library developers
- University of Alabama in Huntsville

## 📖 Citations

If you use this toolkit in your research, please cite:

```bibtex
@software{turbulence_data_processing,
  author = {Taul, Bradley},
  title = {Turbulence Data Processing Toolkit},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/Bradley-TaulUAH/Turbulence_Data_Processing}
}
```

## 🔗 Related Resources

- [Phantom Camera Documentation](https://www.phantomhighspeed.com/support)
- [pyphantom GitHub](https://github.com/pyPhotometry/pyphantom)
- [Anaconda Documentation](https://docs.anaconda.com/)

---

**Last Updated:** December 2024
