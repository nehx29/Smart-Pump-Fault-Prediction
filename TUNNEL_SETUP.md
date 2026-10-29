# Cloudflare Quick Tunnel — Wokwi Integration Setup

This guide explains how to connect the Wokwi ESP32 browser simulator to the local Flask backend
using a Cloudflare Quick Tunnel. The tunnel creates a temporary public HTTPS URL that Wokwi can
reach from its browser environment.

---

## Why a tunnel is needed

Wokwi runs inside a browser tab. It cannot reach `localhost` or `127.0.0.1` directly because the
browser's network sandbox prevents cross-origin requests to local ports. A Cloudflare Quick Tunnel
bridges the gap by assigning a public HTTPS URL (e.g. `https://xxx.trycloudflare.com`) that
forwards traffic to the Flask server running on your machine.

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| `cloudflared` binary | Download from [cloudflare.com/products/tunnel](https://www.cloudflare.com/products/tunnel/) — no account needed for Quick Tunnels |
| Flask backend running | `python app.py` in the `backend/` directory |
| Python 3.x + dependencies | `pip install -r backend/requirements.txt` |

`cloudflared-windows-amd64.exe` is already present at `C:\Users\HP\Downloads\cloudflared-windows-amd64.exe`.

---

## Step-by-step workflow

### Terminal 1 — start the Flask backend

```powershell
cd "C:\Users\HP\OneDrive\Desktop\Smart-Pump-Fault-Prediction\backend"
python app.py
```

Leave this terminal open. The backend binds to `0.0.0.0:5000`.

---

### Terminal 2 — start the Cloudflare tunnel

```powershell
C:\Users\HP\Downloads\cloudflared-windows-amd64.exe tunnel --url http://127.0.0.1:5000
```

After a few seconds the tunnel prints a line like:

```
https://xxxx-yyyy-zzzz.trycloudflare.com
```

**Copy that entire URL.** It changes every time you restart the tunnel.

---

### Terminal 3 — verify the public endpoint

```powershell
# Replace with your actual tunnel URL
$url = "https://xxxx-yyyy-zzzz.trycloudflare.com"
python -c "import requests; r = requests.get('$url/api/health'); print(r.status_code, r.json())"
```

Expected output:
```
200 {'model_loaded': True, 'service': 'smart-pump-backend', 'status': 'ok'}
```

If this fails, see the Troubleshooting section below.

---

### Update the Wokwi sketch

Open `esp32/wokwi_sketch.ino`. The sketch ships with both URL constants **empty** (`""`).
Paste your fresh tunnel URL into both:

```cpp
static const char* CLOUDFLARE_HOST = "https://xxxx-yyyy-zzzz.trycloudflare.com";
static const char* SERVER_URL      = "https://xxxx-yyyy-zzzz.trycloudflare.com/api/sensor-data";
```

> The sketch validates the URL at startup: if either constant is empty or still contains `xxxx`,
> the simulation will print sensor readings locally but skip all HTTP sends, with a clear message.
> This prevents silent failures from stale URLs.

---

### Run the Wokwi simulation

1. Open [wokwi.com](https://wokwi.com) and load the project (or create a new ESP32 project and
   paste the contents of `esp32/wokwi_sketch.ino`).
2. Add three potentiometers in the diagram — one each for GPIO 34, 35, and 32.
3. Click **Run** (▶). The Serial Monitor should print:

```
==========================================
 Smart Pump Monitoring
 ESP32 Wokwi simulator
 Data source: WOKWI_SIMULATED
==========================================
[WiFi] Connecting to Wokwi-GUEST...
[WiFi] Connected.
[HTTP] Endpoint: https://xxxx-yyyy-zzzz.trycloudflare.com/api/sensor-data

------------------------------------------
Pressure ADC: 1037 | 3.800 bar
Current ADC:  819  | 5.000 A
Vibration ADC: 245 | 1.199 mm/s
[HTTP] Sending: {"pump_id":"PUMP-001","pressure":3.8,"current":5.0,"vibration":1.2,"data_source":"WOKWI_SIMULATED"}
[HTTP] Status code: 201
[SUCCESS] Backend returned a successful response.
[RESULT] Pump condition: Normal
[RESULT] Confidence: 100.00%
```

A 201 response confirms the reading was stored. Open the dashboard and Refresh to see it appear
labelled **Wokwi simulator**.

---

## Potentiometer slider positions for known conditions

The ADC range is 0–4095 mapped to the physical maximum via `(adc / 4095) × MAX`.

| Condition | GPIO 34 Pressure | GPIO 35 Current | GPIO 32 Vibration |
|-----------|-----------------|-----------------|-------------------|
| Normal | ~25% (3.8 bar) | ~20% (5.0 A) | ~6% (1.2 mm/s) |
| High Pressure Fault | ~45% (6.75 bar) | ~25% (6.1 A) | ~14% (2.8 mm/s) |
| Overcurrent Fault | ~20% (3.0 bar) | ~37% (9.3 A) | ~17% (3.4 mm/s) |
| Excessive Vibration | ~22% (3.3 bar) | ~22% (5.5 A) | ~34% (6.8 mm/s) |
| Combined Fault | ~8% (1.2 bar) | ~34% (8.5 A) | ~38% (7.6 mm/s) |

---

## Troubleshooting

| Problem | Likely cause | Fix |
|---------|-------------|-----|
| Tunnel log: `cloudflared does not support loading the system root certificate pool` | Windows TLS CA warning — informational only, not fatal in recent versions | Ignore the warning if QUIC shows `Registered tunnel connection` |
| `[HTTP][ERROR] Request failed: -1` in Wokwi serial | SERVER_URL not updated, or tunnel expired | Restart cloudflared, copy new URL, update sketch, restart simulation |
| Serial shows `[HTTP] Skipping send because SERVER_URL is not set` | Both URL constants are still empty `""` | Paste the tunnel URL into both constants and save |
| Wokwi connects but Flask logs nothing | Tunnel is routing to wrong port | Confirm `--url http://127.0.0.1:5000` matches Flask port |
| `404 Endpoint not found` | Wrong path in SERVER_URL | Must end in `/api/sensor-data` exactly |
| Readings always show `Normal` | Potentiometer sliders at 0 (ADC=0) produces 0,0,0 inputs which the model classifies as Normal | Adjust sliders per the table above |

---

## Important limitations

- **Quick tunnels expire.** The subdomain is regenerated every time `cloudflared` restarts. You must
  update the sketch and restart the Wokwi simulation each time.
- **Wokwi sessions are stateless.** Closing or refreshing the browser tab ends the simulation.
- **Not production.** Quick Tunnels are intended for development. For a permanent deployment,
  create a named tunnel in your Cloudflare account with a fixed domain.

---

## Payload schema (what the sketch sends)

```json
POST https://xxxx.trycloudflare.com/api/sensor-data
Content-Type: application/json

{
  "pump_id":     "PUMP-001",
  "pressure":    3.80,
  "current":     5.00,
  "vibration":   1.20,
  "data_source": "WOKWI_SIMULATED"
}
```

The `pump_id` field is accepted and silently ignored by the backend (not stored). The three sensor
fields and `data_source` are stored in SQLite. A successful response is HTTP 201:

```json
{
  "success": true,
  "message": "Sensor reading processed and stored successfully.",
  "data": {
    "id": 42,
    "pressure": 3.80,
    "current": 5.00,
    "vibration": 1.20,
    "data_source": "WOKWI_SIMULATED",
    "prediction": "Normal",
    "confidence": 1.0,
    "timestamp": "2026-10-29 13:45:09"
  }
}
```
