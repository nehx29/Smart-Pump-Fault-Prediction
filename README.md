# Smart Pump Fault Prediction

**Domain:** Predictive Maintenance — Sensor-Driven Fault Classification  

---

## Project Overview

An end-to-end system that monitors industrial pump health and predicts fault conditions using a trained classification model. The system supports two data modes:

- **SIMULATED** — Sensor values generated programmatically for development and testing
- **ESP32** — Real analog sensor readings from physical hardware (ready for deployment)

---

## System Architecture

```
[ PUMP HARDWARE / SENSOR SIMULATOR ]
              │
  ┌───────────┼───────────┐
  ↓           ↓           ↓
Pressure   Current   Vibration
Sensor     Sensor    Sensor
  └───────────┼───────────┘
              ↓
      [ ESP32 Node / Simulator ]
              ↓
        Wi-Fi / REST API
              ↓
    POST http://localhost:5000/api/sensor-data
              ↓
       [ Flask Backend ]
              ↓
   ┌──────────┴──────────┐
   ↓                     ↓
SQLite DB         StandardScaler
(stored)          Preprocessing
                        ↓
                 [ DNN Model ]
              (pump_fault_model.keras)
                        ↓
                 [ Prediction ]
                        ↓
     ┌──────────────────┴──────────────────┐
     ↓                                     ↓
[ React Dashboard ]              [ Alert System ]
(Live charts, history)           (Fault notifications)
```

---

## Project Structure

```
Smart-Pump-Fault-Prediction/
├── backend/                  # Flask REST API Server
│   ├── app.py                # Flask app entry point
│   ├── config.py             # Configuration constants
│   ├── database.py           # SQLite initialization & queries
│   ├── requirements.txt      # Python dependencies
│   ├── routes/
│   │   ├── health.py         # GET /api/health
│   │   ├── sensor.py         # POST /api/sensor-data, GET /api/latest, GET /api/history
│   │   └── prediction.py     # GET /api/predict-manual
│   ├── services/
│   │   ├── prediction_service.py  # DNN inference bridge
│   │   └── sensor_service.py      # Data validation & DB storage
│   ├── test_phase4.py        # Phase 4 API integration tests
│   └── test_phase6.py        # Phase 6 ESP32 compatibility tests
│
├── ml-model/                 # Machine Learning Pipeline
│   ├── dataset/
│   │   └── pump_sensor_dataset.csv  # 3500 sample training dataset
│   ├── preprocessing.py      # Reusable StandardScaler + LabelEncoder
│   ├── train.py              # DNN training script (Keras)
│   ├── evaluate.py           # Model evaluation & metrics
│   └── saved_model/
│       ├── pump_fault_model.keras   # Trained DNN model
│       ├── scaler.pkl               # Fitted StandardScaler
│       ├── label_encoder.pkl        # Fitted LabelEncoder
│       ├── preprocessor.joblib      # Full preprocessor pipeline
│       ├── classes.json             # Class label mapping
│       └── evaluation_metrics.json  # Test accuracy/metrics
│
├── simulator/                # Sensor Simulation Layer
│   └── simulate_sensor.py    # Continuous sensor stream (SIMULATED mode)
│
├── frontend/                 # React Dashboard (Vite)
│   ├── src/
│   │   ├── App.jsx           # Main app + routing + simulation loop
│   │   ├── index.css         # Global design system / dark theme
│   │   ├── components/       # Reusable UI components
│   │   │   ├── Header.jsx
│   │   │   ├── SensorCard.jsx
│   │   │   ├── LiveChart.jsx
│   │   │   ├── HistoryTable.jsx
│   │   │   ├── AlertBanner.jsx
│   │   │   ├── SimulationControl.jsx
│   │   │   └── StatusBadge.jsx
│   │   ├── pages/            # Page-level views
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── SensorMonitoringPage.jsx
│   │   │   ├── PredictionPage.jsx
│   │   │   ├── AlertsPage.jsx
│   │   │   ├── ModelInfoPage.jsx
│   │   │   └── SystemInfoPage.jsx
│   │   └── services/
│   │       └── api.js        # Axios API client
│   └── package.json
│
└── esp32/                    # ESP32 Firmware (Hardware Integration)
    ├── pump_sensor.ino       # Arduino sketch — ready for deployment
    └── README.md             # Wiring, calibration, setup guide
```

---

## Fault Detection Model Summary

| Property | Value |
|----------|-------|
| Framework | TensorFlow / Keras |
| Architecture | Sequential classifier |
| Input Features | pressure, current, vibration (3 features) |
| Hidden Layers | 3 layers (128 → 64 → 32 neurons, ReLU + Dropout) |
| Output | 5-class softmax |
| Dataset | 3,500 samples (70/15/15 split) |
| Optimizer | Adam |
| Loss Function | Categorical Cross-Entropy |

### Fault Classes
1. **Normal**
2. **High Pressure Fault**
3. **Overcurrent Fault**
4. **Excessive Vibration Fault**
5. **Combined Fault**

---

## Quick Start

### 1. Install Python dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the Flask backend
```bash
cd backend
python app.py
```
Backend runs at: `http://127.0.0.1:5000`

### 3. Start the React frontend (development)
```bash
cd frontend
npm install
npm run dev
```
Dashboard opens at: `http://localhost:5173`

### 4. (Optional) Run the sensor simulator
```bash
cd simulator
python simulate_sensor.py
```

### 5. (Optional) Run Phase 6 ESP32 compatibility tests
```bash
cd backend
python -X utf8 test_phase6.py
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Backend and model health check |
| POST | `/api/sensor-data` | Submit sensor reading (runs DNN inference) |
| GET | `/api/latest` | Get most recent reading from SQLite |
| GET | `/api/history?limit=N` | Get last N readings |

### Sensor Data Payload
```json
{
  "pressure":    3.82,
  "current":     5.04,
  "vibration":   1.28,
  "data_source": "SIMULATED"
}
```
Set `data_source` to `"ESP32"` when transmitting from physical hardware.

---

## Phase Completion Status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Project Structure & Environment Setup | ✅ Complete |
| 2 | Dataset Collection & Preprocessing | ✅ Complete |
| 3 | DNN Model Development & Training | ✅ Complete |
| 4 | Flask Backend & REST API | ✅ Complete |
| 5 | React Dashboard | ✅ Complete |
| 6 | ESP32 Hardware Integration Layer | ✅ Complete |

---

## Hardware Integration Status

> **Physical hardware not yet connected.**
> The system is operating in SIMULATED mode.
> The ESP32 firmware (`esp32/pump_sensor.ino`) is pre-configured and ready for deployment.
> API compatibility verified: 16/16 Phase 6 tests passed.

---

## Technologies Used

| Layer | Technology |
|-------|-----------|
| IoT Microcontroller | ESP32 Dev Module (planned) |
| Sensor Simulation | Python (NumPy, Requests) |
| ML Framework | TensorFlow 2.x / Keras |
| Backend API | Flask, Flask-CORS |
| Database | SQLite |
| Frontend | React 18 + Vite |
| Charts | Recharts |
| Icons | Lucide React |
| Styling | Vanilla CSS (dark glassmorphism theme) |

---

## Additional Notes

This project demonstrates practical integration of sensor networks, predictive maintenance, and machine-learning-based classification for industrial pump condition monitoring.

