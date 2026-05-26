# Quick Start Guide

## 📦 Installation (5 minutes)

### Step 1: Navigate to Project Directory
```bash
cd /Users/harshkansara/Documents/bhabhi/Data_house/disease_analysis_project
```

### Step 2: Create Virtual Environment
```bash
# Create venv
python -m venv venv

# Activate venv
source venv/bin/activate
# On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation
```bash
python -c "import pandas; import numpy; import matplotlib; print('✓ All dependencies installed')"
```

---

## 🚀 Running the Analysis

### Option A: Full Pipeline (Recommended)
```bash
python main.py
```
- Loads data
- Calculates all 20 indicators
- Generates visualizations
- Produces analysis report
- **Time:** ~5-10 minutes

### Option B: Analysis Only (Fast)
```bash
python main.py analysis
```
- Loads data
- Calculates indicators
- Generates analysis report
- **No visualizations**
- **Time:** ~1-2 minutes

### Option C: Visualizations Only
```bash
python main.py visualizations
```
- Loads data
- Generates all charts
- Saves to `outputs/charts/`
- **No analysis report**
- **Time:** ~3-5 minutes

---

## 📂 File Organization

```
disease_analysis_project/
├── config.py               ← Configuration & constants
├── data_loader.py          ← Data loading & preprocessing
├── indicators.py           ← All 20 health indicators
├── visualizations.py       ← Chart generation
├── analysis.py             ← Analysis & reporting
├── main.py                 ← Main pipeline
├── requirements.txt        ← Dependencies
├── README.md               ← Full documentation
├── QUICKSTART.md           ← This file
│
├── data/                   ← Place CSV files here
│   ├── china_disease_data_Cleaned.csv
│   └── indicator-formula-calculation-20.csv
│
└── outputs/                ← Generated files
    └── charts/             ← Saved visualizations
        ├── 01_monthly_trends.png
        ├── 02_seasonal_distribution.png
        └── ... more charts
```

---

## 🔍 What Gets Generated

### Console Output
- Data summary statistics
- Quality checks
- All 20 indicator values
- Comprehensive analysis report
- Evidence-based recommendations

### Chart Files (9+)
- `01_monthly_trends.png` - Temporal patterns
- `02_seasonal_distribution.png` - Seasonal breakdown
- `03_urban_rural.png` - Urban vs Rural
- `04_top_10_provinces.png` - Top provinces
- `05_age_gender_distribution.png` - Demographics
- `06_mortality_by_age.png` - Age-specific
- `07_vaccination_impact_cases_deaths.png` - Vaccination
- `08_cfr_by_disease.png` - Disease severity
- `09_disease_month_heatmap.png` - Temporal×Disease

---

## ⚡ Troubleshooting

### Problem: "Module not found" Error
**Solution:** Reinstall dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Problem: Data file not found
**Solution:** Ensure CSV files are in `data/` folder
```bash
ls data/  # Check if files exist
# If not, copy them from parent directory:
cp ../china_disease_data_*.csv data/
cp ../indicator-formula-calculation-20.csv data/
```

### Problem: Charts not saving
**Solution:** Check write permissions
```bash
chmod 755 outputs/
chmod 755 outputs/charts/
```

### Problem: Memory error with large data
**Solution:** Run analysis only (no visualizations)
```bash
python main.py analysis
```

---

## 📊 Sample Output

### Console Output Sample:
```
====================================================================================================
CHINESE DISEASE DATA ANALYSIS - COMPLETE PIPELINE
====================================================================================================

[PHASE 1: DATA LOADING & PREPROCESSING]
----------------------------------------------------------------------------------------------------
✓ Data loaded successfully from data/china_disease_data_ Cleaned.csv
  Shape: 1000 rows × 25 columns

✓ No missing values found

✓ DATA PREPROCESSING COMPLETED
✓ Converted Yes/No to binary (0/1)
✓ Created derived columns: Month_Year, Active_Cases, Quarantine_Days
✓ Processed data shape: (1000, 28)

[PHASE 2: HEALTH INDICATORS CALCULATION]
====================================================================================================
[Calculating Indicators 1-6: Disease Severity & Outcomes]
  ✓ Indicators 1-6: Complete
[Calculating Indicators 7, 8, 15: Control Measures]
  ✓ Indicators 7, 8, 15: Complete
...
✓ ALL 20 INDICATORS CALCULATED SUCCESSFULLY

[ANALYSIS RESULTS]
Case Fatality Rate by Disease:
             Disease   CFR_%
0           Influenza    2.15
1           Measles      1.85
...
```

---

## 🎯 Common Use Cases

### Use Case 1: Quick Metrics Check
```bash
python main.py analysis
# Reviews indicators and generates quick report
# Time: 1-2 minutes
```

### Use Case 2: Generate Charts for Presentation
```bash
python main.py visualizations
# Creates all charts, saves to outputs/charts/
# Time: 3-5 minutes
```

### Use Case 3: Full Academic Submission
```bash
python main.py
# Complete analysis with all indicators, visualizations, and report
# Time: 5-10 minutes
```

---

## 🔧 Customization

### Modify Color Scheme
Edit `config.py`:
```python
COLORS_VACCINATION = ['#FF0000', '#00FF00']  # Red, Green
COLORS_SEASON = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
```

### Change Figure Sizes
Edit `config.py`:
```python
FIGURE_SIZE_DEFAULT = (16, 8)  # Wider figures
FIGURE_SIZE_LARGE = (20, 10)
```

### Enable/Disable Progress Messages
Edit `config.py`:
```python
VERBOSE = False  # Suppress progress output
```

---

## 📚 Python Usage Examples

### Example 1: Use modules independently
```python
from data_loader import get_clean_data
from indicators import HealthIndicators

# Load data
df = get_clean_data()

# Calculate indicators
calc = HealthIndicators(df)
calc.calculate_all()

# Get specific indicator
cfr = calc.get_indicator(3)
print(cfr)
```

### Example 2: Custom analysis
```python
from data_loader import get_clean_data
from analysis import DiseaseAnalyzer

df = get_clean_data()
analyzer = DiseaseAnalyzer(df)

# Run specific analysis
severity = analyzer.analyze_disease_severity()
print(severity)
```

### Example 3: Generate specific visualization
```python
from data_loader import get_clean_data
from visualizations import DiseaseVisualizer

df = get_clean_data()
viz = DiseaseVisualizer(df)

# Generate specific chart
viz.plot_vaccination_impact()
viz.plot_cfr_comparison()
```

---

## ✅ Verification Checklist

Before submission, verify:
- [ ] All 20 indicators calculated
- [ ] All visualizations generated
- [ ] Analysis report complete
- [ ] Recommendations produced
- [ ] Console output captured
- [ ] Charts saved to `outputs/charts/`
- [ ] No errors in execution
- [ ] Data matches source files

---

## 📞 Getting Help

1. **Check the data is correct** in `data/` folder
2. **Review error messages** in console output
3. **Check README.md** for detailed documentation
4. **Verify Python version** (3.7+): `python --version`
5. **Update dependencies:** `pip install --upgrade -r requirements.txt`

---

## 🎓 For Academic Submission

This project is ready for submission as-is.

What's included:
- ✓ All 20 health indicators
- ✓ 9+ professional visualizations
- ✓ Comprehensive analysis report
- ✓ Evidence-based recommendations
- ✓ Complete documentation
- ✓ Reproducible code
- ✓ Quality checks

Ready to use:
```bash
python main.py
```

---

**Questions?** Check README.md or review config.py for settings.

**Happy analyzing!** 🎉
