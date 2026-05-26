# Detailed Installation & Setup Guide

## System Requirements

### Minimum Requirements
- **Operating System**: Windows, macOS, or Linux
- **Python Version**: 3.7 or higher (3.10+ recommended)
- **RAM**: 2GB minimum (4GB+ recommended)
- **Disk Space**: 500MB for project and dependencies

### Recommended Setup
- **Python**: 3.10 or 3.11
- **RAM**: 8GB+
- **Disk Space**: 2GB+ for output files
- **OS**: macOS or Linux for best compatibility

## Pre-Installation Checklist

- [ ] Python 3.7+ is installed
- [ ] pip is available and up-to-date
- [ ] You have CSV data file ready (china_disease_data.csv)
- [ ] You have adequate disk space
- [ ] Internet connection (for downloading packages)

## Step-by-Step Installation

### 1. Verify Python Installation

```bash
# Check Python version
python --version
# or
python3 --version

# Should show Python 3.7 or higher
```

**If Python is not installed**:
- **Windows**: Download from python.org, check "Add Python to PATH"
- **macOS**: Use `brew install python3` or download from python.org
- **Linux**: Use `apt-get install python3` (Ubuntu) or equivalent

---

### 2. Create Virtual Environment (Recommended)

A virtual environment isolates dependencies for this project.

#### On macOS/Linux:
```bash
# Navigate to project directory
cd /Users/harshkansara/Documents/bhabhi/Data_house/disease_analysis_project

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Your prompt should now show (.venv) prefix
```

#### On Windows (Command Prompt):
```bash
cd \path\to\disease_analysis_project

python -m venv .venv

.venv\Scripts\activate.bat
```

#### On Windows (PowerShell):
```bash
cd C:\path\to\disease_analysis_project

python -m venv .venv

.venv\Scripts\Activate.ps1
```

**Troubleshooting Virtual Environment**:
- If `.venv/bin/activate` doesn't work on Windows, try `.venv\Scripts\activate.bat`
- If you get a "permission denied" error, check file permissions
- To deactivate: simply type `deactivate` in terminal

---

### 3. Upgrade pip

```bash
# Ensure pip is up-to-date
pip install --upgrade pip

# Verify upgrade (check version number)
pip --version
```

---

### 4. Install Dependencies

#### Option A: Using requirements.txt (Recommended)

```bash
# Install all dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

#### Option B: Using setup.py

```bash
# Install in development mode
pip install -e .

# Verify installation
pip list
```

#### Option C: Manual Installation

```bash
pip install pandas>=1.3.0
pip install numpy>=1.21.0
pip install matplotlib>=3.4.0
pip install seaborn>=0.11.0
pip install plotly>=5.0.0
pip install scipy>=1.7.0
pip install python-dateutil>=2.8.0
```

**Common Installation Issues**:

| Issue | Solution |
|-------|----------|
| `pip: command not found` | Use `pip3` instead of `pip` |
| `No module named 'pip'` | Run `python -m pip install --upgrade pip` |
| `Permission denied` | Try `pip install --user` or use virtual environment |
| `Incompatible Python version` | Ensure Python 3.7+ is installed |

---

### 5. Prepare Data File

Copy your CSV data file to the expected location:

```bash
# Create data directory if it doesn't exist
mkdir -p data/input

# Copy your CSV file (adjust source path as needed)
cp /path/to/china_disease_data.csv data/input/
```

**Expected CSV Structure**:
- Columns: Province, Disease, Date, Cases, Deaths, Recovered, etc. (25+ columns)
- Format: CSV with headers
- Encoding: UTF-8
- Size: Up to 1GB supported

---

### 6. Verify Installation

```bash
# Check all installed packages
pip list

# Should show:
# - pandas
# - numpy
# - matplotlib
# - seaborn
# - plotly
# - scipy
# - python-dateutil

# Test imports (optional)
python -c "import pandas; print(f'pandas {pandas.__version__}')"
python -c "import numpy; print(f'numpy {numpy.__version__}')"
python -c "import matplotlib; print(f'matplotlib {matplotlib.__version__}')"
```

---

## Running the Analysis

### Basic Execution

```bash
# Make sure you're in the project directory
cd /Users/harshkansara/Documents/bhabhi/Data_house/disease_analysis_project

# Make sure virtual environment is activated
# (you should see (.venv) in your prompt)

# Run the analysis
python main.py
```

### What Happens During Execution

1. **Data Loading** (2-5 seconds)
   - Reads CSV file
   - Validates data structure
   - Performs preprocessing

2. **Indicator Calculation** (5-10 seconds)
   - Calculates all 20 health indicators
   - Generates time series data
   - Computes statistics

3. **Visualization Generation** (10-15 seconds)
   - Creates 28+ charts
   - Saves in multiple formats
   - Generates dashboard

4. **Analysis & Reporting** (5-10 seconds)
   - Performs statistical analysis
   - Detects patterns and outbreaks
   - Generates summary reports

5. **Output Writing** (2-5 seconds)
   - Saves all results
   - Creates directory structure
   - Generates logs

**Total Duration**: Typically 20-40 seconds depending on data size and system

---

### Expected Output

After successful execution, you'll see:

```
Output directory structure created:
output/
├── indicators/
│   └── indicators_summary.csv
├── visualizations/
│   ├── temporal/  (7 charts)
│   ├── geographic/  (6 charts)
│   ├── demographic/  (5 charts)
│   ├── vaccination/  (6 charts)
│   └── dashboard/  (4 charts)
└── reports/
    ├── analysis_summary.txt
    ├── key_findings.json
    └── detailed_report.md

Total: 28+ visualization files + data outputs
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue 1: "ModuleNotFoundError: No module named 'pandas'"

**Cause**: Dependencies not installed

**Solution**:
```bash
# Make sure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

#### Issue 2: "FileNotFoundError: china_disease_data.csv"

**Cause**: Data file not in correct location

**Solution**:
```bash
# Create data directory
mkdir -p data/input

# Copy your CSV file
cp /path/to/your/china_disease_data.csv data/input/

# Verify file exists
ls data/input/  # macOS/Linux
# or
dir data\input  # Windows
```

---

#### Issue 3: "PermissionError: [Errno 13] Permission denied"

**Cause**: Cannot write to output directory

**Solution**:
```bash
# Check directory permissions
ls -la output/  # macOS/Linux

# Create output directory with proper permissions
mkdir -p output
chmod 755 output

# Run analysis again
python main.py
```

---

#### Issue 4: "Python version X.Y not supported"

**Cause**: Python version too old

**Solution**:
```bash
# Check current Python version
python --version

# If too old:
# - Install Python 3.10+ from python.org
# - Or use pyenv: brew install pyenv
# - Or use conda: conda create -n disease-analysis python=3.10
```

---

#### Issue 5: "pip: command not found" or "pip3: command not found"

**Cause**: pip not in PATH

**Solution**:
```bash
# Use Python module directly
python -m pip install -r requirements.txt

# Or reinstall Python with pip option checked
```

---

#### Issue 6: "ModuleNotFoundError" for numpy, matplotlib, etc.

**Cause**: Virtual environment not activated

**Solution**:
```bash
# Verify virtual environment is active (should see (.venv) in prompt)
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# If not active, activate it
# Then run: python main.py
```

---

### Performance Issues

#### Slow Data Loading
- **Cause**: Large CSV file
- **Solution**: 
  - Check available disk space
  - Close other applications
  - System with more RAM recommended

#### Slow Visualization Generation
- **Cause**: Too many charts or large dataset
- **Solution**:
  - Edit `visualizations.py` to skip some charts
  - Use subset of data for testing
  - Run on faster computer

#### Out of Memory Error
- **Cause**: Dataset too large for available RAM
- **Solution**:
  - Increase available system RAM
  - Split data into smaller chunks
  - Process only subset of years/provinces

---

## Advanced Setup Options

### Using Conda (Alternative)

```bash
# Create conda environment
conda create -n disease-analysis python=3.10

# Activate environment
conda activate disease-analysis

# Install dependencies
pip install -r requirements.txt

# Run analysis
python main.py
```

---

### Using Docker (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t disease-analysis .
docker run -v $(pwd)/data:/app/data disease-analysis
```

---

### IDE Setup (VS Code)

1. **Open project folder**: File → Open Folder
2. **Select Python interpreter**: 
   - Command Palette → "Python: Select Interpreter"
   - Choose `.venv` environment
3. **Run in terminal**:
   - Terminal → New Terminal
   - Terminal auto-selects correct environment

---

## Verifying Complete Setup

Run this verification script:

```bash
# Copy this code into verify_setup.py

import sys
import subprocess

def verify_installation():
    """Verify all dependencies are installed"""
    
    modules = [
        'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly', 'scipy'
    ]
    
    print("Checking Python version...")
    if sys.version_info < (3, 7):
        print(f"❌ Python 3.7+ required. Current: {sys.version}")
        return False
    print(f"✓ Python {sys.version}")
    
    print("\nChecking required packages...")
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"❌ {module} - Not installed")
            return False
    
    print("\nChecking data directory...")
    import os
    if os.path.exists('data/input/china_disease_data.csv'):
        print("✓ Data file found")
    else:
        print("⚠ Data file not found - expected at: data/input/china_disease_data.csv")
    
    print("\n✓ All checks passed! Ready to run.")
    return True

if __name__ == "__main__":
    verify_installation()
```

Run verification:
```bash
python verify_setup.py
```

---

## Next Steps

After successful installation:

1. **Review Documentation**:
   - Read `README.md` for project overview
   - Check `PROJECT_STRUCTURE.md` for code organization

2. **Run Analysis**:
   ```bash
   python main.py
   ```

3. **Examine Results**:
   - Check `output/` directory
   - Review visualizations
   - Read generated reports

4. **Customize** (Optional):
   - Edit `config.py` for different parameters
   - Modify `visualizations.py` for custom charts
   - Update `analysis.py` for new analyses

---

## Getting Help

### Resources

- **Python Official**: https://python.org
- **pip Documentation**: https://pip.pypa.io
- **pandas Documentation**: https://pandas.pydata.org
- **matplotlib Gallery**: https://matplotlib.org/gallery

### If You're Stuck

1. **Check the logs**: `logs/analysis.log`
2. **Read error messages carefully** - they usually indicate the problem
3. **Verify your data format** matches expected structure
4. **Test individually**:
   ```bash
   python -c "import pandas; print(pandas.__version__)"
   ```
5. **Search online** for specific error messages

---

## Uninstalling / Cleanup

If you need to remove the project:

```bash
# Remove virtual environment
rm -rf .venv  # macOS/Linux
# or
rmdir /s .venv  # Windows

# Remove generated outputs
rm -rf output/ logs/

# Remove installed packages (if using conda)
conda remove -n disease-analysis --all
```

---

**Last Updated**: 2024  
**Support**: For issues, consult README.md and logs/analysis.log
