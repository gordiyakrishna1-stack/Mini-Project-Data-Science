# Contributing & Development Guide

## Project Development Overview

This document provides guidelines for developers who want to contribute to or customize the Disease Analysis project.

## Code Organization Philosophy

The project follows these principles:

- **Modularity**: Each component handles one responsibility
- **Reusability**: Functions and classes can be used independently
- **Documentation**: Code is well-documented with docstrings
- **Testing**: All major components are testable
- **Maintainability**: Clear structure and naming conventions

## Development Workflow

### 1. Setting Up Development Environment

```bash
# Clone/navigate to project
cd disease_analysis_project

# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Install dependencies with dev tools
pip install -r requirements.txt
pip install pytest pytest-cov black flake8  # Optional dev tools

# Verify setup
python main.py --help
```

### 2. Project Structure Quick Reference

```
disease_analysis_project/
├── config.py              ← Global constants and settings
├── data_loader.py         ← Data input and preprocessing
├── indicators.py          ← Health metric calculations (20 indicators)
├── visualizations.py      ← Chart and graph generation
├── analysis.py            ← Statistical analysis and insights
├── main.py                ← Orchestration and entry point
├── utils.py               ← Helper functions
└── tests/ (optional)      ← Unit tests
```

## Module Development Guide

### Adding a New Health Indicator

**Location**: `indicators.py`

**Steps**:

1. **Add method to `IndicatorCalculator` class**:

```python
def your_new_indicator(self, data: pd.DataFrame) -> float:
    """
    Calculate Your New Indicator.
    
    Formula: (description of calculation)
    Units: (measurement units)
    Range: (expected range, e.g., 0-100%)
    
    Args:
        data: DataFrame containing case information
        
    Returns:
        float: Calculated indicator value
        
    Raises:
        ValueError: If required columns are missing
    """
    required_cols = ['column1', 'column2']
    if not all(col in data.columns for col in required_cols):
        raise ValueError(f"Missing required columns: {required_cols}")
    
    # Your calculation logic here
    result = (data['column1'].sum() / data['column2'].sum()) * 100
    
    return result
```

2. **Register in `calculate_all()` method**:

```python
def calculate_all(self):
    """Calculate all indicators"""
    return {
        'existing_indicator_1': self.existing_indicator_1(self.data),
        'existing_indicator_2': self.existing_indicator_2(self.data),
        'your_new_indicator': self.your_new_indicator(self.data),  # Add here
    }
```

3. **Update documentation** in README.md

4. **Test the indicator**:

```python
# In test or main.py
from indicators import IndicatorCalculator

ic = IndicatorCalculator(test_data)
result = ic.your_new_indicator(test_data)
print(f"New indicator value: {result}")
```

### Adding a New Visualization

**Location**: `visualizations.py`

**Steps**:

1. **Add method to `Visualizer` class**:

```python
def your_new_chart(self, data: pd.DataFrame, title: str = None) -> None:
    """
    Generate your new chart type.
    
    Args:
        data: Processed DataFrame with indicators
        title: Custom chart title
    """
    import matplotlib.pyplot as plt
    
    # Prepare data
    plot_data = data.groupby('Province')['Cases'].sum()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(plot_data.index, plot_data.values)
    ax.set_title(title or 'Your New Chart Title')
    ax.set_xlabel('Province')
    ax.set_ylabel('Cases')
    
    # Save
    output_path = f"{self.output_dir}/your_new_chart.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: {output_path}")
```

2. **Add to `generate_all()` method**:

```python
def generate_all(self):
    """Generate all visualizations"""
    self.temporal_trends()
    self.geographic_analysis()
    self.demographic_insights()
    self.your_new_chart(self.data)  # Add here
    self.print_summary()
```

3. **Test the visualization**:

```python
from visualizations import Visualizer

viz = Visualizer(test_data)
viz.your_new_chart(test_data)
# Check output directory for generated image
```

### Customizing Analysis Engine

**Location**: `analysis.py`

**Steps**:

1. **Add analysis method**:

```python
def your_analysis(self) -> dict:
    """
    Perform your custom analysis.
    
    Returns:
        dict: Analysis results with keys and values
    """
    insights = {}
    
    # Your analysis logic
    insights['metric1'] = self.data['column1'].mean()
    insights['metric2'] = self.data['column2'].max()
    
    return insights
```

2. **Call from main analysis**:

```python
def get_comprehensive_analysis(self) -> dict:
    """Get all analyses"""
    analyses = {
        'existing_analysis': self.existing_analysis(),
        'your_analysis': self.your_analysis(),  # Add here
    }
    return analyses
```

## Modifying Configuration

**Location**: `config.py`

Common customizations:

```python
# Change output directory
OUTPUT_DIR = '/custom/output/path'

# Add new disease types
DISEASES = [
    'Influenza',
    'COVID-19', 
    'Measles',
    'YOUR_NEW_DISEASE'  # Add here
]

# Modify age groups
AGE_GROUPS = ['0-10', '11-20', '21-30', '31-40', '41+']  # Custom bins

# Add new regions
REGION_CODES = {
    'Beijing': 'BJ',
    'Shanghai': 'SH',
    'YOUR_REGION': 'YR'  # Add here
}

# Visualization settings
VISUALIZATION_SETTINGS = {
    'style': 'seaborn-v0_8-darkgrid',
    'dpi': 300,
    'figsize': (12, 6),
    'colormap': 'viridis',
    'YOUR_SETTING': 'YOUR_VALUE'  # Add here
}
```

## Data Processing Pipeline

### Understanding DataLoader

```python
from data_loader import DataLoader

loader = DataLoader()

# Step 1: Load raw CSV
df = loader.load_data('path/to/data.csv')

# Step 2: Validate structure
loader.validate_data(df)

# Step 3: Preprocess (clean, transform, standardize)
df = loader.preprocess(df)

# Step 4: Apply domain transformations
df = loader.apply_transformations(df)

# Result: Ready for analysis
```

### Custom Preprocessing

Edit `data_loader.py`:

```python
def apply_transformations(self, data: pd.DataFrame) -> pd.DataFrame:
    """Apply domain-specific transformations"""
    
    # Existing transformations
    data['Date'] = pd.to_datetime(data['Date'])
    
    # Add your custom transformation
    data['YOUR_CALCULATED_COLUMN'] = data['Column1'] / data['Column2']
    
    return data
```

## Testing Your Changes

### Unit Testing Example

Create `test_indicators.py`:

```python
import unittest
import pandas as pd
from indicators import IndicatorCalculator

class TestNewIndicator(unittest.TestCase):
    
    def setUp(self):
        """Create test data"""
        self.test_data = pd.DataFrame({
            'Cases': [10, 20, 30],
            'Deaths': [1, 2, 3],
            'Province': ['A', 'B', 'C']
        })
        self.calculator = IndicatorCalculator(self.test_data)
    
    def test_your_new_indicator(self):
        """Test your new indicator"""
        result = self.calculator.your_new_indicator(self.test_data)
        
        # Assert expected behavior
        self.assertIsInstance(result, (int, float))
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 100)
    
    def test_missing_columns(self):
        """Test error handling"""
        bad_data = self.test_data.drop('Cases', axis=1)
        
        with self.assertRaises(ValueError):
            self.calculator.your_new_indicator(bad_data)

if __name__ == '__main__':
    unittest.main()
```

Run tests:

```bash
python -m pytest test_indicators.py -v
```

## Code Style Guidelines

### Naming Conventions

```python
# Variables: lowercase_with_underscores
disease_count = 100
mortality_rate = 0.05

# Functions: lowercase_with_underscores
def calculate_mortality_rate():
    pass

# Classes: CamelCase
class IndicatorCalculator:
    pass

# Constants: UPPERCASE_WITH_UNDERSCORES
MAX_AGE = 100
AGE_GROUPS = ['0-14', '15-24']
```

### Documentation Standards

```python
def calculate_rate(numerator: int, denominator: int) -> float:
    """
    Calculate a rate as percentage.
    
    This is a one-line summary. Extended description goes here if needed,
    providing context and important details.
    
    Args:
        numerator (int): Number of cases in numerator
        denominator (int): Total population
        
    Returns:
        float: Rate as percentage (0-100)
        
    Raises:
        ValueError: If denominator is zero
        TypeError: If inputs are not numeric
        
    Examples:
        >>> calculate_rate(10, 100)
        10.0
        >>> calculate_rate(5, 10)
        50.0
    """
    if denominator == 0:
        raise ValueError("Denominator cannot be zero")
    return (numerator / denominator) * 100
```

### Import Organization

```python
# Standard library imports first
import os
import json
from typing import Dict, List

# Third-party imports
import pandas as pd
import numpy as np
from scipy import stats

# Local imports
from config import OUTPUT_DIR
from utils import save_results
```

## Performance Optimization

### Profiling Code

```python
import cProfile
import pstats

# Profile main execution
cProfile.run('main.main()', 'output.prof')

# View results
stats = pstats.Stats('output.prof')
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 functions
```

### Optimization Tips

```python
# Use vectorized operations (Good)
df['rate'] = (df['cases'] / df['population']) * 100

# Avoid loops (Bad)
# for idx, row in df.iterrows():
#     rate = (row['cases'] / row['population']) * 100

# Use list comprehension (Good)
results = [calculate(x) for x in data if x > threshold]

# Avoid repeated function calls (Good)
logger = logging.getLogger(__name__)
logger.info("Message")

# Avoid repeated creation (Bad)
# for item in data:
#     logger = logging.getLogger(__name__)
#     logger.info("Message")
```

## Version Control Best Practices

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/add-new-indicator

# Make changes
git add .

# Commit with clear message
git commit -m "Add new health indicator: XYZ
- Implements formula according to WHO guidelines
- Includes validation and error handling
- Adds visualization in geographic section"

# Push and create pull request
git push origin feature/add-new-indicator
```

### Commit Message Template

```
[Type] Brief description - 50 chars max

Longer explanation if needed. Explain what and why, not how.
- Point 1
- Point 2

Fixes #123
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `perf`

## Documentation Requirements

For any new feature:

1. **Code Comments**: 
   - Explain WHY, not WHAT
   - Use docstrings for all public functions

2. **README Updates**:
   - Add new feature to feature list
   - Include in usage examples

3. **CHANGELOG Entry**:
   - Brief description of change
   - Version and date

## Debugging Techniques

### Using Logging

```python
import logging

logger = logging.getLogger(__name__)

def process_data(data):
    logger.debug(f"Processing {len(data)} records")
    logger.info("Starting data validation")
    
    if invalid:
        logger.warning("Found invalid records, attempting recovery")
    
    if critical_error:
        logger.error("Critical error occurred", exc_info=True)
```

### Interactive Debugging

```python
# Add breakpoint in code
def calculate(x):
    import pdb; pdb.set_trace()  # Execution pauses here
    return x * 2

# Then in Python:
# (Pdb) x  # Print variable
# (Pdb) n  # Next line
# (Pdb) c  # Continue execution
# (Pdb) h  # Help
```

## Release Checklist

Before releasing new version:

- [ ] All tests pass: `pytest`
- [ ] Code is formatted: `black .`
- [ ] No lint issues: `flake8 .`
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version bumped in `setup.py`
- [ ] All dependencies specified in `requirements.txt`

## Troubleshooting Development Issues

### Module Not Found

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Import Errors

```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Ensure module is in path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Changes Not Taking Effect

```bash
# Reload modules in Python
import importlib
import your_module
importlib.reload(your_module)
```

## Resources for Developers

### Documentation
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [NumPy Documentation](https://numpy.org/doc/)
- [Matplotlib Guide](https://matplotlib.org/stable/contents.html)
- [Python Best Practices](https://pep8.org/)

### Tools
- **Testing**: pytest, unittest
- **Linting**: flake8, pylint
- **Formatting**: black, autopep8
- **Documentation**: Sphinx, MkDocs

## Questions or Ideas?

- Create an issue for bugs
- Propose features with examples
- Submit pull requests with tests
- Keep discussions professional and constructive

## License

See LICENSE file in project root.

---

**Last Updated**: 2024
**Version**: 1.0.0
