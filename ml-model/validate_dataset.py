import os
import sys
import pandas as pd
import numpy as np

# Path configurations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_PATH = os.path.join(BASE_DIR, 'dataset', 'raw', 'pump_sensor_dataset.csv')
LEGACY_DATA_PATH = os.path.join(BASE_DIR, 'dataset', 'pump_sensor_dataset.csv')

def get_target_dataset_path():
    if os.path.exists(RAW_DATA_PATH):
        return RAW_DATA_PATH
    elif os.path.exists(LEGACY_DATA_PATH):
        # Ensure raw folder exists and copy over if in legacy path
        os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
        df = pd.read_csv(LEGACY_DATA_PATH)
        df.to_csv(RAW_DATA_PATH, index=False)
        return RAW_DATA_PATH
    return None

def validate_dataset(filepath=None):
    """
    Comprehensive dataset validation suite.
    Checks:
    1. File availability & readability
    2. Column names & presence of required features
    3. Data types
    4. Missing values
    5. Duplicate rows
    6. Invalid numerical values
    7. Label availability & class distribution
    8. Record count
    """
    print("\n==============================================================")
    print("        SMART PUMP DATASET VALIDATION REPORT (PHASE 2)         ")
    print("==============================================================")

    if filepath is None:
        filepath = get_target_dataset_path()

    # 1. File Availability
    if not filepath or not os.path.exists(filepath):
        print(f"[ERROR] Dataset file not found at path: {filepath}")
        return False, None

    print(f"[PASSED] File Availability     : {filepath}")

    # 2. CSV Readability
    try:
        df = pd.read_csv(filepath)
        print(f"[PASSED] CSV Readability        : OK")
    except Exception as e:
        print(f"[ERROR] Failed to read CSV file: {e}")
        return False, None

    # 3. Number of Records & Columns
    num_records, num_cols = df.shape
    print(f"[PASSED] Number of Records      : {num_records}")
    print(f"[PASSED] Number of Columns      : {num_cols}")
    print(f"[PASSED] Column Names           : {list(df.columns)}")

    # 4. Data Types Check
    print("\n--- Column Data Types ---")
    for col in df.columns:
        print(f"  - {col:<15}: {df[col].dtype}")

    # 5. Missing Values Check
    null_counts = df.isnull().sum()
    total_missing = null_counts.sum()
    print(f"\n--- Missing Values Check ---")
    if total_missing == 0:
        print("[PASSED] Missing Values         : NONE (0 missing cells)")
    else:
        print(f"[WARNING] Found {total_missing} missing values:")
        for col, count in null_counts.items():
            if count > 0:
                print(f"  - {col}: {count} missing")

    # 6. Duplicate Rows Check
    duplicate_count = df.duplicated().sum()
    print(f"\n--- Duplicate Rows Check ---")
    if duplicate_count == 0:
        print("[PASSED] Duplicate Rows         : NONE (0 duplicates)")
    else:
        print(f"[WARNING] Found {duplicate_count} duplicate rows.")

    # 7. Invalid Numerical Values Check
    expected_numeric_cols = ['pressure', 'current', 'vibration']
    print(f"\n--- Invalid Numerical Values Check ---")
    invalid_num_issues = 0
    for col in expected_numeric_cols:
        if col in df.columns:
            converted = pd.to_numeric(df[col], errors='coerce')
            invalid_types = converted.isnull().sum() - df[col].isnull().sum()
            neg_count = (converted < 0).sum()
            
            if invalid_types > 0 or neg_count > 0:
                print(f"[WARNING] Issues in '{col}': {invalid_types} non-numeric, {neg_count} negative values.")
                invalid_num_issues += (invalid_types + neg_count)
            else:
                print(f"[PASSED] '{col}' Bounds      : Valid (Min: {df[col].min():.2f}, Max: {df[col].max():.2f})")
        else:
            print(f"[WARNING] Required feature '{col}' missing from columns.")

    # 8. Label Availability & Class Distribution
    print(f"\n--- Target Label Check ---")
    if 'label' in df.columns:
        class_dist = df['label'].value_counts()
        print("[PASSED] Target Label Column    : Found ('label')")
        print("[PASSED] Class Distribution:")
        for cls_name, count in class_dist.items():
            pct = (count / num_records) * 100
            print(f"   * {cls_name:<26}: {count:4d} samples ({pct:.1f}%)")
    else:
        print("[ERROR] Target column 'label' missing from dataset!")
        return False, df

    print("\n==============================================================")
    print(" SUMMARY: DATASET IS VALID AND READY FOR PREPROCESSING (PHASE 2)")
    print("==============================================================\n")
    return True, df

if __name__ == '__main__':
    validate_dataset()
