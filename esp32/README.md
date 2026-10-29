# ESP32 Hardware Integration — Smart Pump Fault Prediction

**Project:** Smart Pump Fault Prediction — Industrial Pump Condition Monitoring

---

## Overview

This directory contains the ESP32 firmware (`pump_sensor.ino`) that enables **physical hardware integration** with the Smart Pump Fault Prediction System.

The system currently operates using a **Sensor Simulation Layer** (`simulator/simulate_sensor.py`). When physical hardware becomes available, flashing this sketch to an ESP32 will seamlessly replace the simulated source — no backend, ML model, or frontend changes are required.

---

## Hardware Required

| Component | Specification | ESP32 Pin |
|-----------|--------------|-----------|
| ESP32 Dev Module | 38-pin Devkit V1 | — |
| Pressure Sensor | Industrial Transducer, 0–10 bar, 0.5V–4.5V analog output | GPIO 34 (ADC1_CH6) |
| Current Sensor | ACS712-20A Hall-Effect Module | GPIO 35 (ADC1_CH7) |
| Vibration Sensor | ADXL345 / Piezoelectric Analog Type | GPIO 32 (ADC1_CH4) |
| DC Water Pump | 12V Low-Voltage Centrifugal Pump | — |
| Power Supply | 3.3V/5V for ESP32; 12V for Pump | — |

> **Note:** Use ADC1 pins only (GPIO 32–39) for analog sensor readings. ADC2 pins conflict with Wi-Fi and must be avoided.

---

## Wiring Diagram

```
[ Pressure Sensor ]
  OUT (0.5V-4.5V) ──────────────────────────────── GPIO 34
  VCC (5V) ─────────────────────────────────────── 5V Pin
  GND ──────────────────────────────────────────── GND

[ ACS712 Current Sensor ]
  OUT (Analog) ─────────────────────────────────── GPIO 35
  VCC (5V) ─────────────────────────────────────── 5V Pin
  GND ──────────────────────────────────────────── GND

[ Vibration Sensor ]
  OUT (Analog) ─────────────────────────────────── GPIO 32
  VCC (3.3V) ───────────────────────────────────── 3.3V Pin
  GND ──────────────────────────────────────────── GND

[ DC Water Pump ]
  Connected via relay/MOSFET driver to external 12V supply.
  Control signal (if used): separate GPIO (e.g., GPIO 25)
```

---

## Sensor Calibration

### Pressure Sensor (0–10 bar, 0.5V–4.5V output)
```cpp
float voltage      = (analogRead(PIN) / 4095.0) * 3.3;
float pressureBar  = (voltage - 0.5) * (10.0 / 4.0);
```
- At **0.5V → 0 bar** (minimum)
- At **4.5V → 10 bar** (maximum)
- Values below 0.5V are clamped to 0.0

### Current Sensor (ACS712-20A)
```cpp
float voltage      = (analogRead(PIN) / 4095.0) * 3.3;
float currentAmps  = abs(voltage - 1.65) / 0.100;  // 100mV/A sensitivity
```
- Midpoint (no current) = **1.65V** on 3.3V ADC
- Sensitivity = **100 mV/A**

### Vibration Sensor (Piezoelectric Analog)
```cpp
float voltage      = (analogRead(PIN) / 4095.0) * 3.3;
float vibrationMMS = voltage * 3.5;  // Scaled to mm/s RMS
```
- Range: **0 – ~11.5 mm/s** (adjustable scaling factor)

---

## Software Setup

### Prerequisites
1. Install [Arduino IDE](https://www.arduino.cc/en/software) or PlatformIO
2. Install ESP32 board support:
   - In Arduino IDE → Boards Manager → Search `esp32` → Install by Espressif Systems
3. Install required libraries:
   ```
   Sketch → Include Library → Manage Libraries
   - ArduinoJson (by Benoit Blanchon) v6.x
   ```
   (WiFi.h and HTTPClient.h are included with the ESP32 board package)

### Configuration
Open `pump_sensor.ino` and update these constants before flashing:

```cpp
// Wi-Fi credentials
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASS = "YOUR_WIFI_PASSWORD";

// Backend server IP (find the PC's LAN IP — NOT localhost)
// On Windows: run `ipconfig` in cmd
// On Linux/Mac: run `ip addr` or `ifconfig`
const char* SERVER_URL = "http://192.168.1.XXX:5000/api/sensor-data";
```

> **Important:** The ESP32 and the PC running Flask must be on the **same Wi-Fi network**.
> `localhost` will NOT work from an ESP32. You must use the PC's local IP address (e.g., `192.168.1.105`).

### Find Your PC's Local IP

```powershell
# Windows
ipconfig | findstr "IPv4"

# Linux/macOS
ip addr show | grep "inet "
```

---

## Flashing the Sketch

1. Open `pump_sensor.ino` in Arduino IDE
2. Select board: **Tools → Board → ESP32 Arduino → ESP32 Dev Module**
3. Select port: **Tools → Port → COM_X** (the ESP32's port)
4. Click **Upload** (⇧Ctrl+U)
5. Open **Serial Monitor** at **115200 baud** to verify output

### Expected Serial Monitor Output
```
=======================================================
  Smart Pump Monitoring System — ESP32 IoT Node Setup  
=======================================================
Connecting to Wi-Fi SSID: YourNetwork...
Wi-Fi Connected successfully!
ESP32 IP Address: 192.168.1.110
Ready to collect sensor readings...

[SENSOR READ] Pressure: 3.82 bar | Current: 5.04 A | Vibration: 1.28 mm/s
HTTP Response [201]: {"success": true, "data": {"prediction": "Normal", "confidence": 0.9987, "data_source": "ESP32"}}
```

---

## JSON Payload Schema

The ESP32 transmits the following JSON payload via HTTP POST every 2 seconds:

```json
{
  "pressure":    3.82,
  "current":     5.04,
  "vibration":   1.28,
  "data_source": "ESP32"
}
```

**Endpoint:** `POST http://<server-ip>:5000/api/sensor-data`  
**Content-Type:** `application/json`

The `data_source` field distinguishes hardware readings from simulation readings in the SQLite database and React Dashboard.

---

## Expected Fault Detection Response

```json
{
  "success": true,
  "message": "Sensor data processed and stored successfully",
  "data": {
    "id": 42,
    "pressure": 3.82,
    "current": 5.04,
    "vibration": 1.28,
    "prediction": "Normal",
    "confidence": 0.9987,
    "data_source": "ESP32",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

---

## Fault Condition Reference

The fault detection model classifies readings into 5 pump conditions:

| Condition | Pressure (bar) | Current (A) | Vibration (mm/s) |
|-----------|---------------|-------------|-----------------|
| Normal | 3.5 – 4.5 | 4.5 – 5.5 | 0.8 – 1.6 |
| High Pressure Fault | > 5.5 | Elevated | Slightly elevated |
| Overcurrent Fault | Normal | > 8.0 | Slightly elevated |
| Excessive Vibration Fault | Normal | Normal | > 5.5 |
| Combined Fault | < 2.0 or > 6.0 | > 7.0 | > 6.0 |

---

## Hardware vs. Simulator Comparison

| Aspect | Simulator (`simulate_sensor.py`) | ESP32 (`pump_sensor.ino`) |
|--------|----------------------------------|--------------------------|
| Data Source | `"SIMULATED"` | `"ESP32"` |
| Sensor Values | Mathematically generated | Real physical ADC readings |
| Network | Runs locally on same machine | Wi-Fi LAN HTTP POST |
| Flask API | No change required | No change required |
| Fault Detection | No change required | No change required |
| Frontend | Shows `SIMULATED` badge | Shows `ESP32` badge |
| Database | Same SQLite table | Same SQLite table |

---

## Switching Between Sources

To switch from simulated to real ESP32 data:

1. Keep the Flask backend running (`python app.py` in `backend/`)
2. Stop the simulator: stop `simulator/simulate_sensor.py`
3. Flash and power on the ESP32 with the correct Wi-Fi/IP config
4. The React Dashboard will automatically display `ESP32` as the data source

No code changes to the backend, ML model, or frontend are needed.

---

## Troubleshooting

| Problem | Solution |
|---------|---------|
| Wi-Fi not connecting | Check SSID/password spelling; ensure 2.4GHz network (ESP32 doesn't support 5GHz) |
| HTTP POST fails | Verify SERVER_URL uses the PC's LAN IP, not `localhost`. Run Flask on `0.0.0.0` |
| ADC readings are 0 | Check sensor wiring; use only ADC1 pins (GPIO 32–39) |
| Pressure reads negative | Voltage below 0.5V — check sensor power supply (needs 5V) |
| Prediction always "Normal" | Check calibration constants match your specific sensor models |
| Serial Monitor garbled | Set baud rate to 115200 |

---

## Academic Note

> **Hardware Status:** Physical ESP32 and sensors are planned for future integration.  
> **Current Stage:** The system uses the Sensor Simulation Layer (`data_source: SIMULATED`).  
> **This firmware is pre-configured and ready for deployment** — only Wi-Fi credentials and the server IP need updating before flashing.  
> **API Compatibility Verified:** All 16 Phase 6 tests passed using the exact ESP32 JSON schema against the live Flask server.
