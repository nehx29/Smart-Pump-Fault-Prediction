import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_PATH = os.path.join(BASE_DIR, 'dataset', 'raw', 'pump_sensor_dataset.csv')
LEGACY_DATA_PATH = os.path.join(BASE_DIR, 'dataset', 'pump_sensor_dataset.csv')
PROCESSED_DIR = os.path.join(BASE_DIR, 'dataset', 'processed')
SAVED_MODEL_DIR = os.path.join(BASE_DIR, 'saved_model')

SCALER_PATH = os.path.join(SAVED_MODEL_DIR, 'scaler.pkl')
ENCODER_PATH = os.path.join(SAVED_MODEL_DIR, 'label_encoder.pkl')
PREPROCESSOR_JOBLIB_PATH = os.path.join(SAVED_MODEL_DIR, 'preprocessor.joblib')
CLASSES_PATH = os.path.join(SAVED_MODEL_DIR, 'classes.json')

FEATURE_COLUMNS = ['pressure', 'current', 'vibration']
TARGET_COLUMN = 'label'

# Physical sensor bounds for data validation
SENSOR_BOUNDS = {
    'pressure': (0.0, 15.0),    # bar
    'current': (0.0, 25.0),     # Amperes
    'vibration': (0.0, 20.0)    # mm/s
}

def validate_sensor_reading(pressure, current, vibration):
    """
    Validates sensor values against physical bounds.
    Returns (is_valid, sanitized_dict or error_message)
    """
    try:
        p = float(pressure)
        c = float(current)
        v = float(vibration)
    except (ValueError, TypeError):
        return False, "Pressure, current, and vibration must be numeric values."

    if not (SENSOR_BOUNDS['pressure'][0] <= p <= SENSOR_BOUNDS['pressure'][1]):
        return False, f"Pressure {p} out of valid bounds {SENSOR_BOUNDS['pressure']}"
    if not (SENSOR_BOUNDS['current'][0] <= c <= SENSOR_BOUNDS['current'][1]):
        return False, f"Current {c} out of valid bounds {SENSOR_BOUNDS['current']}"
    if not (SENSOR_BOUNDS['vibration'][0] <= v <= SENSOR_BOUNDS['vibration'][1]):
        return False, f"Vibration {v} out of valid bounds {SENSOR_BOUNDS['vibration']}"

    return True, {'pressure': p, 'current': c, 'vibration': v}

class PumpDataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.is_fitted = False

    def load_raw_dataset(self, filepath=None):
        """Loads dataset from raw directory or legacy path."""
        if filepath is None:
            if os.path.exists(RAW_DATA_PATH):
                filepath = RAW_DATA_PATH
            elif os.path.exists(LEGACY_DATA_PATH):
                os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
                df = pd.read_csv(LEGACY_DATA_PATH)
                df.to_csv(RAW_DATA_PATH, index=False)
                filepath = RAW_DATA_PATH
            else:
                raise FileNotFoundError("Raw pump dataset not found!")

        df = pd.read_csv(filepath)
        return df

    def clean_dataset(self, df):
        """
        Handles missing values and cleans invalid numbers.
        """
        df_clean = df.dropna(subset=FEATURE_COLUMNS + [TARGET_COLUMN]).copy()
        
        # Coerce and clip numeric features
        for col in FEATURE_COLUMNS:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            min_val, max_val = SENSOR_BOUNDS[col]
            # Remove rows out of physical range
            df_clean = df_clean[(df_clean[col] >= min_val) & (df_clean[col] <= max_val)]

        return df_clean

    def process_and_split(self, test_size=0.15, val_size=0.15, seed=42):
        """
        Executes full preprocessing pipeline without data leakage:
        1. Clean data
        2. Encode target labels
        3. Stratified Train / Val / Test split
        4. Fit StandardScaler ONLY on X_train
        5. Transform X_train, X_val, X_test using fitted scaler
        6. Save processed splits and preprocessor objects
        """
        print("\n--- Running Preprocessing Pipeline (Phase 2) ---")
        df_raw = self.load_raw_dataset()
        df_clean = self.clean_dataset(df_raw)
        
        print(f"Dataset cleaned: {len(df_clean)} valid rows out of {len(df_raw)} raw rows.")

        X_unscaled = df_clean[FEATURE_COLUMNS].values
        y_raw = df_clean[TARGET_COLUMN].values

        # Label Encoding
        y_encoded = self.label_encoder.fit_transform(y_raw)
        
        # Stratified Split into Train (70%), Val (15%), Test (15%)
        X_train_val, X_test_unscaled, y_train_val, y_test = train_test_split(
            X_unscaled, y_encoded, test_size=test_size, random_state=seed, stratify=y_encoded
        )
        
        val_relative_size = val_size / (1.0 - test_size)
        X_train_unscaled, X_val_unscaled, y_train, y_val = train_test_split(
            X_train_val, y_train_val, test_size=val_relative_size, random_state=seed, stratify=y_train_val
        )

        # STRICT DATA LEAKAGE PREVENTION: Fit scaler ONLY on X_train!
        print("[GUARD] Data Leakage Prevention: Fitting StandardScaler strictly on Training set.")
        X_train = self.scaler.fit_transform(X_train_unscaled)
        X_val = self.scaler.transform(X_val_unscaled)
        X_test = self.scaler.transform(X_test_unscaled)
        
        self.is_fitted = True

        # Save preprocessor artifacts
        self.save_artifacts()

        # Save processed split CSVs into ml-model/dataset/processed/
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        
        train_df = pd.DataFrame(X_train, columns=FEATURE_COLUMNS)
        train_df['label'] = y_train
        train_df.to_csv(os.path.join(PROCESSED_DIR, 'train.csv'), index=False)

        val_df = pd.DataFrame(X_val, columns=FEATURE_COLUMNS)
        val_df['label'] = y_val
        val_df.to_csv(os.path.join(PROCESSED_DIR, 'val.csv'), index=False)

        test_df = pd.DataFrame(X_test, columns=FEATURE_COLUMNS)
        test_df['label'] = y_test
        test_df.to_csv(os.path.join(PROCESSED_DIR, 'test.csv'), index=False)

        print(f"[SUCCESS] Saved processed dataset splits to {PROCESSED_DIR}")
        print(f"  - Train set : {len(train_df)} samples (70%)")
        print(f"  - Val set   : {len(val_df)} samples (15%)")
        print(f"  - Test set  : {len(test_df)} samples (15%)\n")

        return (X_train, y_train), (X_val, y_val), (X_test, y_test)

    def transform_single(self, pressure, current, vibration):
        """
        Preprocesses a single live sensor reading for real-time inference.
        """
        if not self.is_fitted:
            self.load_artifacts()
            
        features = np.array([[float(pressure), float(current), float(vibration)]])
        scaled_features = self.scaler.transform(features)
        return scaled_features

    def save_artifacts(self, target_dir=SAVED_MODEL_DIR):
        """Saves preprocessor objects to disk."""
        os.makedirs(target_dir, exist_ok=True)
        joblib.dump(self.scaler, SCALER_PATH)
        joblib.dump(self.label_encoder, ENCODER_PATH)
        joblib.dump(self, PREPROCESSOR_JOBLIB_PATH)
        
        classes_dict = {int(i): str(cls_name) for i, cls_name in enumerate(self.label_encoder.classes_)}
        with open(CLASSES_PATH, 'w') as f:
            json.dump(classes_dict, f, indent=2)
            
        print(f"[SUCCESS] Saved fitted scaler, label encoder, and preprocessor object to {target_dir}")

    def load_artifacts(self, target_dir=SAVED_MODEL_DIR):
        """Loads fitted scaler and encoder objects."""
        if not os.path.exists(SCALER_PATH) or not os.path.exists(ENCODER_PATH):
            raise FileNotFoundError("Preprocessor artifacts missing. Run preprocessing pipeline first.")
            
        self.scaler = joblib.load(SCALER_PATH)
        self.label_encoder = joblib.load(ENCODER_PATH)
        self.is_fitted = True
        return self

if __name__ == '__main__':
    preprocessor = PumpDataPreprocessor()
    preprocessor.process_and_split()
