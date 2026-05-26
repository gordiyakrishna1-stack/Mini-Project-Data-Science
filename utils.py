"""
Utility Functions for Disease Analysis Project
Helper functions for common tasks
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from config import OUTPUT_DIR, CHARTS_DIR


def create_directories():
    """Ensure all required directories exist"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    CHARTS_DIR.mkdir(exist_ok=True)
    return True


def get_timestamp():
    """Get current timestamp string"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_dataframe(df, filename, directory=OUTPUT_DIR, format='csv'):
    """Save dataframe to file"""
    filepath = directory / f"{filename}.{format}"
    
    if format == 'csv':
        df.to_csv(filepath, index=False)
    elif format == 'excel':
        df.to_excel(filepath, sheet_name='Sheet1', index=False)
    elif format == 'json':
        df.to_json(filepath, orient='records', indent=2)
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    return filepath


def load_dataframe(filename, directory=OUTPUT_DIR, format='csv'):
    """Load dataframe from file"""
    filepath = directory / f"{filename}.{format}"
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    if format == 'csv':
        return pd.read_csv(filepath)
    elif format == 'excel':
        return pd.read_excel(filepath)
    elif format == 'json':
        return pd.read_json(filepath)
    else:
        raise ValueError(f"Unsupported format: {format}")


def print_section(title, width=100):
    """Print formatted section header"""
    print("\n" + "=" * width)
    print(f"{title:^{width}}")
    print("=" * width)


def print_subsection(title, width=100):
    """Print formatted subsection header"""
    print("\n" + "-" * width)
    print(f"{title:<{width}}")
    print("-" * width)


def format_number(num, thousand_sep=True):
    """Format number with thousands separator"""
    if thousand_sep:
        return f"{int(num):,}"
    return str(int(num))


def calculate_percentage(numerator, denominator, decimals=2):
    """Calculate percentage safely"""
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, decimals)


def get_summary_stats(series):
    """Get summary statistics for a series"""
    return {
        'count': series.count(),
        'mean': series.mean(),
        'median': series.median(),
        'std': series.std(),
        'min': series.min(),
        'max': series.max(),
        'q25': series.quantile(0.25),
        'q75': series.quantile(0.75)
    }


def normalize_column(df, column):
    """Normalize column to 0-1 range"""
    min_val = df[column].min()
    max_val = df[column].max()
    if max_val == min_val:
        return df[column].copy()
    return (df[column] - min_val) / (max_val - min_val)


def standardize_column(df, column):
    """Standardize column to mean=0, std=1"""
    mean = df[column].mean()
    std = df[column].std()
    if std == 0:
        return df[column].copy()
    return (df[column] - mean) / std


def identify_outliers(series, method='iqr', threshold=1.5):
    """Identify outliers using IQR or Z-score method"""
    if method == 'iqr':
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        return series[(series < lower_bound) | (series > upper_bound)]
    
    elif method == 'zscore':
        mean = series.mean()
        std = series.std()
        z_scores = np.abs((series - mean) / std)
        return series[z_scores > threshold]
    
    else:
        raise ValueError(f"Unknown method: {method}")


def generate_report_section(title, data, format='text'):
    """Generate formatted report section"""
    if format == 'text':
        print_section(title)
        if isinstance(data, pd.DataFrame):
            print(data.to_string(index=False))
        elif isinstance(data, dict):
            for key, value in data.items():
                print(f"{key:<30}: {value}")
        else:
            print(data)
    
    elif format == 'markdown':
        print(f"\n## {title}\n")
        if isinstance(data, pd.DataFrame):
            print(data.to_markdown(index=False))
        elif isinstance(data, dict):
            for key, value in data.items():
                print(f"- **{key}:** {value}")
        else:
            print(data)


def merge_results(*dataframes):
    """Merge multiple dataframes"""
    return pd.concat(dataframes, axis=0, ignore_index=True)


def filter_by_column(df, column, values):
    """Filter dataframe by column values"""
    if isinstance(values, (list, tuple)):
        return df[df[column].isin(values)]
    else:
        return df[df[column] == values]


def get_unique_values(df, column, sort=False):
    """Get unique values from column"""
    unique = df[column].unique()
    if sort:
        return sorted(unique)
    return unique


def count_by_column(df, column):
    """Count values by column"""
    return df[column].value_counts().to_frame('Count').reset_index()


def create_backup(filepath):
    """Create backup of file"""
    backup_path = f"{filepath}.backup_{get_timestamp()}"
    if os.path.exists(filepath):
        os.rename(filepath, backup_path)
        return backup_path
    return None


def validate_data_integrity(df, required_columns=None):
    """Validate dataframe integrity"""
    checks_passed = []
    
    # Check if dataframe is empty
    if df.empty:
        return False, ["Dataframe is empty"]
    
    # Check required columns
    if required_columns:
        missing = set(required_columns) - set(df.columns)
        if missing:
            return False, [f"Missing columns: {missing}"]
        checks_passed.append("All required columns present")
    
    # Check for duplicates
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        checks_passed.append(f"⚠ Found {duplicates} duplicate rows")
    else:
        checks_passed.append("No duplicate rows")
    
    # Check for null values
    nulls = df.isnull().sum().sum()
    if nulls > 0:
        checks_passed.append(f"⚠ Found {nulls} null values")
    else:
        checks_passed.append("No null values")
    
    return True, checks_passed


def print_data_summary(df):
    """Print comprehensive data summary"""
    print_section("DATA SUMMARY")
    print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"\nColumns:")
    for col in df.columns:
        print(f"  {col:<25} {df[col].dtype}")
    
    print(f"\nMemory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print(f"\nFirst row:")
    print(df.iloc[0])


def export_analysis_results(results, filename):
    """Export analysis results to multiple formats"""
    # Save as CSV
    if isinstance(results, dict):
        for key, df in results.items():
            if isinstance(df, pd.DataFrame):
                save_dataframe(df, f"{filename}_{key}", format='csv')
    else:
        save_dataframe(results, filename, format='csv')


# Decorator for timing execution
def timer_decorator(func):
    """Decorator to time function execution"""
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"⏱ {func.__name__} completed in {elapsed:.2f} seconds")
        return result
    return wrapper


# Example usage:
# @timer_decorator
# def slow_function():
#     pass
