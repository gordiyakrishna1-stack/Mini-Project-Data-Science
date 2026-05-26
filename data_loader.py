"""
Data Loading & Preprocessing Module
Handles CSV loading, data quality checks, and data transformations
"""

import pandas as pd
import numpy as np
from config import DATA_FILE, YES_NO_COLUMNS, VERBOSE


class DataLoader:
    """Loads and preprocesses disease data"""
    
    def __init__(self, filepath=DATA_FILE):
        self.filepath = filepath
        self.df_raw = None
        self.df_processed = None
        
    def load_data(self):
        """Load CSV data"""
        try:
            self.df_raw = pd.read_csv(self.filepath)
            if VERBOSE:
                print(f"✓ Data loaded successfully from {self.filepath}")
                print(f"  Shape: {self.df_raw.shape[0]} rows × {self.df_raw.shape[1]} columns")
            return self.df_raw
        except FileNotFoundError:
            print(f"✗ Error: File not found at {self.filepath}")
            raise
    
    def quality_check(self):
        """Perform data quality checks"""
        if self.df_raw is None:
            print("✗ No data loaded. Call load_data() first.")
            return False
        
        print("\n" + "="*80)
        print("DATA QUALITY ASSESSMENT")
        print("="*80)
        
        # Null values
        null_counts = self.df_raw.isnull().sum()
        if null_counts.sum() == 0:
            print("✓ No missing values found")
        else:
            print(f"⚠ Missing values detected:\n{null_counts[null_counts > 0]}")
        
        # Unique values
        print("\n✓ Unique values per column:")
        for col in self.df_raw.columns:
            print(f"   {col}: {self.df_raw[col].nunique()} unique values")
        
        # Basic stats
        print("\n✓ Data types:")
        print(self.df_raw.dtypes)
        
        return True
    
    def preprocess(self):
        """Convert Yes/No to binary, create derived columns"""
        if self.df_raw is None:
            print("✗ No data loaded. Call load_data() first.")
            return False
        
        self.df_processed = self.df_raw.copy()
        
        # Convert Yes/No to binary (0/1)
        for col in YES_NO_COLUMNS:
            if col in self.df_processed.columns:
                self.df_processed[col] = (self.df_processed[col] == 'Yes').astype(int)
        
        # Create derived columns
        self.df_processed['Month_Year'] = (
            self.df_processed['Month'].astype(str) + '-' + 
            self.df_processed['Year'].astype(str)
        )
        self.df_processed['Active_Cases'] = (
            self.df_processed['Reported_Cases'] - self.df_processed['Recovered']
        )
        self.df_processed['Quarantine_Days'] = (
            self.df_processed['Days_Hospitalized'] * 0.5
        )
        
        if VERBOSE:
            print("\n" + "="*80)
            print("DATA PREPROCESSING COMPLETED")
            print("="*80)
            print("✓ Converted Yes/No to binary (0/1)")
            print("✓ Created derived columns: Month_Year, Active_Cases, Quarantine_Days")
            print(f"✓ Processed data shape: {self.df_processed.shape}")
        
        return True
    
    def get_data(self):
        """Return processed data"""
        if self.df_processed is None:
            print("✗ Data not processed yet. Call preprocess() first.")
            return None
        return self.df_processed
    
    def get_raw_data(self):
        """Return raw data"""
        return self.df_raw
    
    def summary_statistics(self):
        """Print summary statistics"""
        if self.df_processed is None:
            return False
        
        print("\n" + "="*80)
        print("SUMMARY STATISTICS")
        print("="*80)
        print(self.df_processed.describe())
        return True


def get_clean_data(filepath=DATA_FILE):
    """Convenience function to load and preprocess data in one call"""
    loader = DataLoader(filepath)
    loader.load_data()
    loader.quality_check()
    loader.preprocess()
    return loader.get_data()
