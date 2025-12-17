# Environment Setup Guide

This guide will walk you through setting up the Python environment needed to run the Turbulence Data Processing toolkit using Anaconda and VS Code.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installing Anaconda](#installing-anaconda)
3. [Installing Phantom SDK](#installing-phantom-sdk)
4. [Creating the Conda Environment](#creating-the-conda-environment)
5. [Installing Python Dependencies](#installing-python-dependencies)
6. [Installing pyphantom](#installing-pyphantom)
7. [Setting Up VS Code](#setting-up-vs-code)
8. [Verifying Installation](#verifying-installation)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Operating System**: Windows 10/11 (required for Phantom SDK)
- **Disk Space**: ~5 GB for Anaconda + dependencies
- **Administrator Access**: Required for Phantom SDK installation

---

## Installing Anaconda

### Step 1: Download Anaconda

1. Go to [https://www.anaconda.com/download](https://www.anaconda.com/download)
2. Download the **Windows 64-bit** installer (Python 3.x)
3. Run the installer (`Anaconda3-XXXX.XX-Windows-x86_64.exe`)

### Step 2: Install Anaconda

1. Click **Next** through the welcome screens
2. Accept the license agreement
3. Choose installation type:
   - **Just Me** (recommended) - No admin rights needed
   - **All Users** - Requires administrator rights
4. Choose installation location (default is fine):
   ```
   C:\Users\<YourUsername>\anaconda3
   ```
5. **Important**: On the "Advanced Installation Options" page:
   - ✅ **Check** "Add Anaconda3 to my PATH environment variable" (ignore the warning)
   - ✅ **Check** "Register Anaconda3 as my default Python"
6. Click **Install** (takes ~10 minutes)
7. Click **Finish**

### Step 3: Verify Anaconda Installation

1. Open **Anaconda Prompt** (search for it in Start menu)
2. Type:
   ```bash
   conda --version
   ```
   You should see something like: `conda 24.1.2`

---

## Installing Phantom SDK

The Phantom SDK is required for `pyphantom` to read `.cine` video files.

### Step 1: Download Phantom Camera Control (PCC)

1. Go to Vision Research's website: [https://www.phantomhighspeed.com/support/software](https://www.phantomhighspeed.com/support/software)
2. Download **Phantom Camera Control (PCC) 4.5** or later
   - File name: `PCC_4.5_Setup.exe` (or similar)
3. You may need to create a Vision Research account to download

### Step 2: Install PCC

1. Run `PCC_4.5_Setup.exe` as Administrator
2. Follow the installation wizard:
   - Accept the license agreement
   - Choose installation directory (default recommended):
     ```
     C:\Program Files\Phantom\Phantom Camera Control\4.5\
     ```
   - Select "Full Installation" (includes SDK)
3. Click **Install**
4. Restart your computer after installation

### Step 3: Verify SDK Installation

1. Navigate to:
   ```
   C:\Program Files\Phantom\Phantom Camera Control\4.5\
   ```
2. Verify these folders exist:
   - `bin\` - Contains DLL files
   - `include\` - Contains header files
   - `lib\` - Contains library files

### Step 4: Add SDK to PATH (Critical!)

1. Open **System Environment Variables**:
   - Press `Windows Key`, search for "Environment Variables"
   - Click "Edit the system environment variables"
   - Click **Environment Variables** button
2. Under "System variables", find `Path` and click **Edit**
3. Click **New** and add:
   ```
   C:\Program Files\Phantom\Phantom Camera Control\4.5\bin
   ```
4. Click **OK** on all windows
5. **Restart** your computer for changes to take effect

---

## Creating the Conda Environment

### Step 1: Clone the Repository

1. Open **Anaconda Prompt**
2. Navigate to where you want the code:
   ```bash
   cd C:\Users\<YourUsername>\Documents
   ```
3. Clone the repository:
   ```bash
   git clone https://github.com/Bradley-TaulUAH/Turbulence_Data_Processing.git
   cd Turbulence_Data_Processing
   ```

   **If you don't have Git installed:**
   - Download the repository as a ZIP from GitHub
   - Extract to `C:\Users\<YourUsername>\Documents\Turbulence_Data_Processing`
   - Open Anaconda Prompt and navigate there:
     ```bash
     cd C:\Users\<YourUsername>\Documents\Turbulence_Data_Processing
     ```

### Step 2: Create the Conda Environment

```bash
conda create -n turbulence python=3.9
```

When prompted `Proceed ([y]/n)?`, type `y` and press Enter.

**What this does:**
- Creates a new isolated Python environment called `turbulence`
- Installs Python 3.9 (compatible with all dependencies)

### Step 3: Activate the Environment

```bash
conda activate turbulence
```

Your prompt should now show `(turbulence)` at the beginning:
```
(turbulence) C:\Users\YourName\Documents\Turbulence_Data_Processing>
```

---

## Installing Python Dependencies

### Step 1: Install from requirements.txt

With the `turbulence` environment activated:

```bash
pip install -r requirements.txt
```

This installs all required packages:
- `numpy` - Numerical computing
- `opencv-python` - Image processing
- `matplotlib` - Plotting
- `scipy` - Scientific computing
- `pandas` - Data manipulation
- And others (see `requirements.txt`)

**Note**: This may take 5-10 minutes depending on your internet speed.

---

## Installing pyphantom

### Step 1: Install pyphantom

```bash
pip install pyphantom
```

### Step 2: Verify Installation

Test that pyphantom can find the Phantom SDK:

```bash
python -c "from pyphantom import Phantom; print('pyphantom installed successfully!')"
```

**If you see an error:**
- Verify Phantom SDK is installed (see [Installing Phantom SDK](#installing-phantom-sdk))
- Verify SDK is in your PATH environment variable
- Restart Anaconda Prompt and try again

---

## Setting Up VS Code

### Step 1: Install Visual Studio Code

1. Download VS Code from [https://code.visualstudio.com/](https://code.visualstudio.com/)
2. Run the installer
3. During installation, check:
   - ✅ "Add to PATH"
   - ✅ "Register Code as an editor for supported file types"
   - ✅ "Add 'Open with Code' action to context menu"
4. Click **Install**

### Step 2: Install Python Extension

1. Open VS Code
2. Click the **Extensions** icon in the left sidebar (or press `Ctrl+Shift+X`)
3. Search for "Python"
4. Install the **Python extension by Microsoft** (it should be the first result)

### Step 3: Open the Project Folder

1. In VS Code, click **File** → **Open Folder**
2. Navigate to:
   ```
   C:\Users\<YourUsername>\Documents\Turbulence_Data_Processing
   ```
3. Click **Select Folder**

### Step 4: Select the Conda Environment

1. Open any Python file (e.g., `Centroid tracker updated.py`)
2. Look at the bottom-right corner of VS Code
3. Click on the Python version (e.g., "Python 3.9.x")
4. A menu will appear at the top showing available Python interpreters
5. Select: `Python 3.9.x ('turbulence')`
   - It should show the full path to your conda environment:
     ```
     C:\Users\<YourUsername>\anaconda3\envs\turbulence\python.exe
     ```

**If you don't see 'turbulence' in the list:**
1. Press `Ctrl+Shift+P` to open Command Palette
2. Type: `Python: Select Interpreter`
3. Click **Enter interpreter path...**
4. Click **Find...**
5. Navigate to:
   ```
   C:\Users\<YourUsername>\anaconda3\envs\turbulence\python.exe
   ```
6. Click **Select Interpreter**

### Step 5: Configure VS Code Terminal to Use Conda

1. Press `Ctrl+Shift+P` to open Command Palette
2. Type: `Terminal: Select Default Profile`
3. Select **Command Prompt** or **PowerShell**
4. Open a new terminal in VS Code (`Ctrl+` ` or Terminal → New Terminal)
5. Activate your environment:
   ```bash
   conda activate turbulence
   ```

**To automatically activate the environment:**
1. In VS Code, go to **File** → **Preferences** → **Settings**
2. Search for: `terminal.integrated.env.windows`
3. Click **Edit in settings.json**
4. Add:
   ```json
   {
       "terminal.integrated.defaultProfile.windows": "Command Prompt",
       "terminal.integrated.profiles.windows": {
           "Command Prompt": {
               "path": "C:\\Windows\\System32\\cmd.exe",
               "args": ["/K", "C:\\Users\\<YourUsername>\\anaconda3\\Scripts\\activate.bat turbulence"]
           }
       }
   }
   ```
   Replace `<YourUsername>` with your actual Windows username.

---

## Verifying Installation

### Complete Verification Script

Create a test file `test_installation.py` with the following:

```python
import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print()

# Test core packages
try:
    import numpy as np
    print(f"✓ NumPy {np.__version__}")
except ImportError:
    print("✗ NumPy not found")

try:
    import cv2
    print(f"✓ OpenCV {cv2.__version__}")
except ImportError:
    print("✗ OpenCV not found")

try:
    import matplotlib
    print(f"✓ Matplotlib {matplotlib.__version__}")
except ImportError:
    print("✗ Matplotlib not found")

try:
    import scipy
    print(f"✓ SciPy {scipy.__version__}")
except ImportError:
    print("✗ SciPy not found")

try:
    from pyphantom import Phantom
    print("✓ pyphantom installed")
    print("  Attempting to initialize Phantom SDK...")
    ph = Phantom()
    print("  ✓ Phantom SDK connection successful!")
    ph.close()
except Exception as e:
    print(f"✗ pyphantom error: {e}")

print("\n=== Installation verification complete ===")
```

Run it:
```bash
python test_installation.py
```

**Expected output:**
```
Python version: 3.9.x ...
Python executable: C:\Users\...\anaconda3\envs\turbulence\python.exe

✓ NumPy 1.26.4
✓ OpenCV 4.10.0.84
✓ Matplotlib 3.10.0
✓ SciPy 1.14.1
✓ pyphantom installed
  Attempting to initialize Phantom SDK...
  ✓ Phantom SDK connection successful!

=== Installation verification complete ===
```

---

## Troubleshooting

### Issue 1: `conda: command not found`

**Solution:**
1. Reopen Anaconda Prompt (not regular Command Prompt)
2. Or add Anaconda to PATH:
   - Open System Environment Variables
   - Add these to PATH:
     ```
     C:\Users\<YourUsername>\anaconda3
     C:\Users\<YourUsername>\anaconda3\Scripts
     C:\Users\<YourUsername>\anaconda3\Library\bin
     ```
   - Restart your terminal

### Issue 2: `ModuleNotFoundError: No module named 'pyphantom'`

**Solution:**
```bash
# Make sure environment is activated
conda activate turbulence

# Reinstall pyphantom
pip uninstall pyphantom
pip install pyphantom
```

### Issue 3: `Phantom SDK not found` error from pyphantom

**Solution:**
1. Verify SDK installation:
   ```
   C:\Program Files\Phantom\Phantom Camera Control\4.5\bin
   ```
2. Check PATH environment variable includes the SDK bin folder
3. Restart your computer after modifying PATH
4. Verify DLL files exist:
   ```
   C:\Program Files\Phantom\Phantom Camera Control\4.5\bin\PhFile.dll
   ```

### Issue 4: VS Code can't find conda environment

**Solution:**
1. Press `Ctrl+Shift+P`
2. Type: `Python: Select Interpreter`
3. If not listed, click **Enter interpreter path...**
4. Manually navigate to:
   ```
   C:\Users\<YourUsername>\anaconda3\envs\turbulence\python.exe
   ```

### Issue 5: Permission errors during pip install

**Solution:**
```bash
# Run Anaconda Prompt as Administrator
# Then retry:
conda activate turbulence
pip install -r requirements.txt
```

### Issue 6: OpenCV import error (DLL load failed)

**Solution:**
Install Visual C++ Redistributable:
1. Download from: [https://aka.ms/vs/17/release/vc_redist.x64.exe](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. Run installer
3. Restart computer

---

## Next Steps

Once your environment is set up, proceed to [QUICKSTART.md](QUICKSTART.md) to process your first dataset!

---

## Quick Reference Commands

```bash
# Activate environment
conda activate turbulence

# Deactivate environment
conda deactivate

# List installed packages
conda list

# Update a package
pip install --upgrade package_name

# Remove environment (if you need to start over)
conda deactivate
conda env remove -n turbulence
```

---

## Additional Resources

- [Anaconda Documentation](https://docs.anaconda.com/)
- [pyphantom GitHub](https://github.com/pyPhotometry/pyphantom)
- [Vision Research Support](https://www.phantomhighspeed.com/support)
- [VS Code Python Tutorial](https://code.visualstudio.com/docs/python/python-tutorial)

---

**Still having issues?** Open an issue on the GitHub repository with:
- Your operating system version
- Output of `conda list`
- Full error message
- Output of `test_installation.py`
