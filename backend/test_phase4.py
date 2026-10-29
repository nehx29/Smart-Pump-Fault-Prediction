import requests
import json
import time
import subprocess
import sys
import os

BASE_URL = "http://127.0.0.1:5000/api"

def run_tests():
    print("==============================================================")
    print("      SMART PUMP FLASK BACKEND INTEGRATION TEST (PHASE 4)     ")
    print("==============================================================")

    # 1. Test GET /api/health
    print("\n--- 1. Testing GET /api/health ---")
    res = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {res.status_code}")
    print(f"Response   : {json.dumps(res.json(), indent=2)}")
    assert res.status_code == 200
    assert res.json()['status'] == 'ok'
    assert res.json()['model_loaded'] is True

    # 2. Test POST /api/predict
    print("\n--- 2. Testing POST /api/predict ---")
    payload_pred = {"pressure": 3.73, "current": 4.79, "vibration": 0.96}
    res = requests.post(f"{BASE_URL}/predict", json=payload_pred)
    print(f"Status Code: {res.status_code}")
    print(f"Response   : {json.dumps(res.json(), indent=2)}")
    assert res.status_code == 200
    assert 'prediction' in res.json()
    assert 'probabilities' in res.json()

    # 3. Test POST /api/sensor-data
    print("\n--- 3. Testing POST /api/sensor-data ---")
    payload_sensor = {
        "pressure": 3.73,
        "current": 4.79,
        "vibration": 0.96,
        "data_source": "SIMULATED"
    }
    res = requests.post(f"{BASE_URL}/sensor-data", json=payload_sensor)
    print(f"Status Code: {res.status_code}")
    print(f"Response   : {json.dumps(res.json(), indent=2)}")
    assert res.status_code == 201
    assert res.json()['success'] is True
    inserted_id = res.json()['data']['id']

    # 4. Test GET /api/latest
    print("\n--- 4. Testing GET /api/latest ---")
    res = requests.get(f"{BASE_URL}/latest")
    print(f"Status Code: {res.status_code}")
    print(f"Response   : {json.dumps(res.json(), indent=2)}")
    assert res.status_code == 200
    assert res.json()['data']['id'] == inserted_id

    # 5. Test GET /api/history
    print("\n--- 5. Testing GET /api/history?limit=10 ---")
    res = requests.get(f"{BASE_URL}/history?limit=10")
    print(f"Status Code: {res.status_code}")
    print(f"Response   : {json.dumps(res.json(), indent=2)}")
    assert res.status_code == 200
    assert res.json()['count'] >= 1

    # 6. Test Invalid Inputs (Missing field, non-numeric, empty JSON)
    print("\n--- 6. Testing Invalid Inputs (HTTP 400 Validation) ---")
    
    # Missing field
    res1 = requests.post(f"{BASE_URL}/predict", json={"pressure": 3.5, "current": 4.8})
    print(f"Missing Field Status: {res1.status_code} | Body: {res1.json()}")
    assert res1.status_code == 400

    # Non-numeric
    res2 = requests.post(f"{BASE_URL}/predict", json={"pressure": "abc", "current": 4.8, "vibration": 1.0})
    print(f"Non-numeric Status  : {res2.status_code} | Body: {res2.json()}")
    assert res2.status_code == 400

    # Empty JSON
    res3 = requests.post(f"{BASE_URL}/predict", json={})
    print(f"Empty JSON Status   : {res3.status_code} | Body: {res3.json()}")
    assert res3.status_code == 400

    print("\n==============================================================")
    print("       ALL API INTEGRATION TESTS PASSED SUCCESSFULLY!          ")
    print("==============================================================\n")

if __name__ == '__main__':
    run_tests()
