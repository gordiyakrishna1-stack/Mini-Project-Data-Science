"""
Configuration & Constants for Chinese Disease Analysis Project
"""

import os
from pathlib import Path

# Project Directories
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
CHARTS_DIR = OUTPUT_DIR / "charts"

# Create directories if they don't exist
OUTPUT_DIR.mkdir(exist_ok=True)
CHARTS_DIR.mkdir(exist_ok=True)

# Data Files
DATA_FILE = DATA_DIR / "china_disease_data_Cleaned.csv"
INDICATOR_REFERENCE_FILE = DATA_DIR / "indicator-formula-calculation-20.csv"

# Visualization Settings
FIGURE_SIZE_DEFAULT = (14, 6)
FIGURE_SIZE_LARGE = (16, 8)
FIGURE_SIZE_SQUARE = (12, 10)

# Color Schemes
COLORS_SEASON = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
COLORS_VACCINATION = ['#e74c3c', '#2ecc71']  # Red for non-vaccinated, Green for vaccinated
COLORS_GENDER = ['#FF69B4', '#4169E1']  # Pink for Female, Blue for Male
COLOR_PALETTE_MAIN = "husl"

# Data Constants
SEASON_ORDER = ['Spring', 'Summer', 'Autumn', 'Winter']
AGE_GROUP_ORDER = ['0-14', '15-24', '25-44', '45-64', '65+']
MONTH_ORDER = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

NUMERIC_COLUMNS = [
    'Reported_Cases', 'Deaths', 'Hospitalized', 'Recovered', 'Month', 'Year',
    'ICU_Admission', 'Symptom_Fever', 'Symptom_Cough', 'Symptom_Rash',
    'Contact_Tracing', 'Lab_Confirmed', 'Follow_Up', 'Days_Hospitalized',
    'Region_Code', 'Travel_History', 'Comorbidity', 'Quarantined', 'Vaccinated'
]

YES_NO_COLUMNS = [
    'Hospitalized', 'Recovered', 'Vaccinated', 'Travel_History', 'Comorbidity',
    'Quarantined', 'ICU_Admission', 'Symptom_Fever', 'Symptom_Cough', 'Symptom_Rash',
    'Contact_Tracing', 'Lab_Confirmed', 'Follow_Up'
]

# Indicator Names
INDICATOR_NAMES = {
    1: "Incidence Rate",
    2: "Prevalence Rate",
    3: "Case Fatality Rate (CFR)",
    4: "Recovery Rate",
    5: "Hospitalization Rate",
    6: "ICU Admission Rate",
    7: "Quarantine Rate",
    8: "Average Days Hospitalized",
    9: "Mortality by Age Group",
    10: "Gender-specific Attack Rate",
    11: "Monthly Case Trend",
    12: "Seasonal Distribution",
    13: "Year-on-Year Growth Rate",
    14: "Peak Month Analysis",
    15: "Outbreak Duration",
    16: "Urban vs Rural Ratio",
    17: "Province-wise Case Density",
    18: "Region Code Distribution",
    19: "Travel-associated Cases",
    20: "Vaccination Impact"
}

# Visualization Settings
FONT_SIZE_TITLE = 14
FONT_SIZE_LABEL = 12
FONT_SIZE_TICK = 10

# DPI for saved figures
DPI_SAVE = 300

# Verbosity
VERBOSE = True

# Export Formats
EXPORT_FORMATS = ['png', 'pdf']
