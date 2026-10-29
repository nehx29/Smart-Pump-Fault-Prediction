# Smart Pump Fault Prediction — Dataset Documentation

**Project:** Smart Pump Fault Prediction — Industrial Pump Condition Monitoring  
**Domain:** Predictive Maintenance — Sensor-Driven Fault Classification

---

## 1. Dataset Overview

* **Dataset Name:** Smart Centrifugal Pump Operational & Fault Condition Monitoring Dataset
* **Source:** Synthetically generated using physics-informed Gaussian distributions modelling known pump fault signatures. Not sourced from an external public dataset.
* **Download / Storage Status:** Localized inside project repository (`ml-model/dataset/raw/pump_sensor_dataset.csv`)
* **Total Records:** 3,500 samples
* **Features:** 3 Continuous Numerical Signals (`pressure`, `current`, `vibration`)
* **Target Label:** Categorical Operating Condition (`label`) with 5 distinct pump fault states

---

## 2. Feature Mapping Table

| Project Feature | Actual Dataset Column | Unit of Measurement | Valid Physical Bounds | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Pressure** | `pressure` | bar | 0.0 – 15.0 bar | Pump discharge line hydrostatic pressure |
| **Current** | `current` | Amperes (A) | 0.0 – 25.0 A | Electric motor stator current draw |
| **Vibration** | `vibration` | mm/s | 0.0 – 20.0 mm/s | Bearing housing RMS vibration velocity |
| **Target Condition** | `label` | String Class Name | Categorical (5 classes) | Pump operational state / fault class |

---

## 3. Class Distribution & Labels

The dataset contains 5 balanced pump operational states (700 samples per class):

1. **`Normal`** (700 samples / 20%): Optimal operation. Pressure ~3.8 bar, Current ~5.0 A, Vibration ~1.2 mm/s.
2. **`High Pressure Fault`** (700 samples / 20%): Discharge restriction / valve blockage. Pressure ~6.4 bar, Current ~6.8 A, Vibration ~2.8 mm/s.
3. **`Overcurrent Fault`** (700 samples / 20%): Motor overload / stalled impeller. Pressure ~3.3 bar, Current ~9.6 A, Vibration ~3.4 mm/s.
4. **`Excessive Vibration Fault`** (700 samples / 20%): Bearing wear / mechanical unbalance. Pressure ~3.6 bar, Current ~5.4 A, Vibration ~6.8 mm/s.
5. **`Combined Fault`** (700 samples / 20%): Low suction pressure (cavitation) with heavy mechanical strain. Pressure ~1.4 bar, Current ~8.4 A, Vibration ~7.5 mm/s.

---

## 4. File Structure & Data Governance

```text
ml-model/dataset/
├── raw/
│   └── pump_sensor_dataset.csv     <-- Unmodified original raw dataset (3,500 samples)
├── processed/
│   ├── train.csv                   <-- Scaled training split (70% = 2,450 samples)
│   ├── val.csv                     <-- Scaled validation split (15% = 525 samples)
│   └── test.csv                    <-- Scaled hold-out test split (15% = 525 samples)
└── dataset_info.md                 <-- Documentation & Feature Schema
```

---

## 5. Missing Values & Validation Findings

* **Missing Values:** 0 missing values across all columns.
* **Duplicate Rows:** 0 duplicate rows detected.
* **Invalid / Negative Values:** 0 invalid or negative numerical values detected.
* **Data Types:** `pressure` (float64), `current` (float64), `vibration` (float64), `label` (object/string).

---

## 6. Preprocessing & Data Leakage Prevention

1. **Cleaning:** Automated validation removes non-numeric or physically impossible out-of-bound values.
2. **Label Encoding:** `LabelEncoder` maps the 5 categorical strings to numerical indices `[0, 1, 2, 3, 4]`.
3. **Stratified Split:** Dataset is split using stratified sampling into:
   - **Train set:** 70% (2,450 samples)
   - **Validation set:** 15% (525 samples)
   - **Test set:** 15% (525 samples)
4. **Data Leakage Guard:** `StandardScaler` is fitted **EXCLUSIVELY on the Training set**. Validation and Test sets are transformed using the pre-fitted training scaler.
5. **Artifact Storage:** Preprocessor objects (`scaler.pkl`, `label_encoder.pkl`, `preprocessor.joblib`, `classes.json`) are serialized into `ml-model/saved_model/`.

---

## 7. Dataset Limitations & Future ESP32 Deployment

* **Current Stage:** Data input layer utilizes the simulated sensor layer (`data_source: "SIMULATED"`).
* **Future Hardware Alignment:** Sensor parameters directly mirror the physical output ranges of the planned ESP32 analog sensors (Pressure Transducer, ACS712 Current Sensor, Piezoelectric/MPU6050 Vibration Sensor).
