import time
import requests
import random
import argparse
import sys
import os

API_ENDPOINT = "http://127.0.0.1:5000/api/sensor-data"

MODES = {
    'NORMAL': {
        'pressure': (3.2, 4.3),
        'current': (4.2, 5.8),
        'vibration': (0.6, 1.8)
    },
    'HIGH_PRESSURE': {
        'pressure': (5.8, 7.5),
        'current': (6.0, 7.8),
        'vibration': (2.0, 3.5)
    },
    'OVERCURRENT': {
        'pressure': (2.8, 4.2),
        'current': (8.8, 11.2),
        'vibration': (2.2, 4.2)
    },
    'HIGH_VIBRATION': {
        'pressure': (3.0, 4.5),
        'current': (4.8, 6.5),
        'vibration': (5.5, 8.8)
    },
    'COMBINED_FAULT': {
        'pressure': (1.0, 2.2),
        'current': (7.5, 9.8),
        'vibration': (6.0, 9.2)
    }
}

def generate_sensor_values(mode):
    if mode == 'RANDOM_DRIFT':
        mode = random.choice(list(MODES.keys()))
        
    bounds = MODES.get(mode, MODES['NORMAL'])
    
    # Generate values with realistic continuous variance/noise
    p = round(random.uniform(*bounds['pressure']) + random.gauss(0, 0.05), 2)
    c = round(random.uniform(*bounds['current']) + random.gauss(0, 0.08), 2)
    v = round(random.uniform(*bounds['vibration']) + random.gauss(0, 0.05), 2)

    return max(0.1, p), max(0.1, c), max(0.1, v)

def send_reading(pressure, current, vibration, endpoint=API_ENDPOINT):
    payload = {
        "pressure": pressure,
        "current": current,
        "vibration": vibration,
        "data_source": "SIMULATED"
    }
    
    try:
        response = requests.post(endpoint, json=payload, timeout=5)
        if response.status_code in [200, 201]:
            res_json = response.json()
            pred = res_json.get('data', {}).get('prediction', 'Unknown')
            conf = res_json.get('data', {}).get('prediction_confidence', 0)
            print(f"[{time.strftime('%H:%M:%S')}] Sent -> P:{pressure:.2f} bar | C:{current:.2f} A | V:{vibration:.2f} mm/s | DNN Prediction: {pred} ({conf}%)")
            return res_json
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Failed with status {response.status_code}: {response.text}")
    except requests.exceptions.ConnectionError:
        print(f"[{time.strftime('%H:%M:%S')}] Connection Error: Unable to reach backend at {endpoint}. Ensure Flask server is running.")
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Error sending sensor data: {e}")
    return None

def run_simulation(mode='NORMAL', interval=2.0, count=None, endpoint=API_ENDPOINT):
    print("==========================================================")
    print("           SMART PUMP IoT SENSOR SIMULATOR                ")
    print("      (Simulated Data Layer - Hardware Stand-in)         ")
    print("==========================================================")
    print(f" Target API Endpoint : {endpoint}")
    print(f" Data Source Marker  : SIMULATED")
    print(f" Selected Mode       : {mode}")
    print(f" Transmission Rate   : Every {interval} seconds")
    print(" Press Ctrl+C to terminate simulation.")
    print("==========================================================\n")

    sent = 0
    try:
        while True:
            p, c, v = generate_sensor_values(mode)
            send_reading(p, c, v, endpoint=endpoint)
            sent += 1
            if count and sent >= count:
                print(f"Simulation completed after sending {count} readings.")
                break
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nSimulator stopped by user.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Smart Pump Sensor Simulator")
    parser.add_argument('--mode', choices=list(MODES.keys()) + ['RANDOM_DRIFT'], default='NORMAL', help="Simulation behavior mode")
    parser.add_argument('--interval', type=float, default=2.0, help="Transmission interval in seconds")
    parser.add_argument('--count', type=int, default=None, help="Number of packets to send (default: continuous)")
    parser.add_argument('--url', type=str, default=API_ENDPOINT, help="Flask API endpoint URL")
    
    args = parser.parse_args()
    run_simulation(mode=args.mode, interval=args.interval, count=args.count, endpoint=args.url)
