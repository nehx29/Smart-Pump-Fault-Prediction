"""
=============================================================================
PHASE 6 - ESP32 HARDWARE COMMUNICATION LAYER
API Compatibility & Integration Tests
=============================================================================
Project      : Smart Pump Fault Prediction System
=============================================================================

This test file verifies that the Flask REST API correctly handles both
SIMULATED and ESP32 data sources without any changes to the backend,
preprocessing pipeline, or DNN model.

All tests are performed using the exact JSON schema that the ESP32 firmware
(esp32/pump_sensor.ino) transmits.
=============================================================================
"""

import sys
import json
import requests

BASE_URL = "http://127.0.0.1:5000"
PASSED = 0
FAILED = 0
RESULTS = []


def test(name, fn):
    global PASSED, FAILED
    try:
        result = fn()
        if result:
            print(f"  [PASS] {name}")
            PASSED += 1
            RESULTS.append((name, "PASS", ""))
        else:
            print(f"  [FAIL] {name}")
            FAILED += 1
            RESULTS.append((name, "FAIL", "Assertion returned False"))
    except Exception as exc:
        print(f"  [ERROR] {name}: {exc}")
        FAILED += 1
        RESULTS.append((name, "ERROR", str(exc)))


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: Health Endpoint
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 65)
print("  PHASE 6 - ESP32 COMPATIBILITY TEST SUITE")
print("  Smart Pump Fault Prediction System")
print("=" * 65)

print("\n[ SECTION 1 ] Health Endpoint")


def test_health_ok():
    r = requests.get(f"{BASE_URL}/api/health", timeout=5)
    d = r.json()
    print(f"    status={d.get('status')}, model_loaded={d.get('model_loaded')}")
    return r.status_code == 200 and d.get("status") == "ok"


test("GET /api/health returns 200 and status=ok", test_health_ok)


def test_health_model_loaded():
    r = requests.get(f"{BASE_URL}/api/health", timeout=5)
    d = r.json()
    return d.get("model_loaded") is True


test("DNN model is loaded (model_loaded=True)", test_health_model_loaded)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: ESP32 Normal Condition Payload
# ─────────────────────────────────────────────────────────────────────────────
print("\n[ SECTION 2 ] ESP32 Normal Condition Payload")

ESP32_NORMAL = {
    "pressure":    3.95,
    "current":     5.12,
    "vibration":   1.35,
    "data_source": "ESP32"
}
_esp32_normal_resp = None


def test_esp32_accepted():
    global _esp32_normal_resp
    r = requests.post(
        f"{BASE_URL}/api/sensor-data",
        json=ESP32_NORMAL,
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    _esp32_normal_resp = r.json()
    print(f"    HTTP {r.status_code} | success={_esp32_normal_resp.get('success')}")
    return r.status_code == 201 and _esp32_normal_resp.get("success") is True


test("POST /api/sensor-data with data_source=ESP32 returns 201", test_esp32_accepted)


def test_esp32_data_source_stored():
    if _esp32_normal_resp is None:
        return False
    ds = _esp32_normal_resp.get("data", {}).get("data_source")
    print(f"    data_source in response: {ds}")
    return ds == "ESP32"


test("Response contains data_source=ESP32", test_esp32_data_source_stored)


def test_esp32_prediction_present():
    if _esp32_normal_resp is None:
        return False
    pred = _esp32_normal_resp.get("data", {}).get("prediction")
    print(f"    DNN prediction: {pred}")
    return pred is not None and isinstance(pred, str) and len(pred) > 0


test("DNN prediction label returned for ESP32 payload", test_esp32_prediction_present)


def test_esp32_confidence_present():
    if _esp32_normal_resp is None:
        return False
    conf = _esp32_normal_resp.get("data", {}).get("confidence")
    print(f"    confidence: {conf}")
    return conf is not None and isinstance(conf, float) and 0.0 <= conf <= 1.0


test("Confidence score present and in range [0, 1]", test_esp32_confidence_present)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: SIMULATED Source Unchanged
# ─────────────────────────────────────────────────────────────────────────────
print("\n[ SECTION 3 ] SIMULATED Source Backward Compatibility")

SIM_NORMAL = {
    "pressure":    3.80,
    "current":     5.00,
    "vibration":   1.20,
    "data_source": "SIMULATED"
}


def test_simulated_still_works():
    r = requests.post(f"{BASE_URL}/api/sensor-data", json=SIM_NORMAL, timeout=5)
    d = r.json()
    print(f"    HTTP {r.status_code} | success={d.get('success')} | source={d.get('data', {}).get('data_source')}")
    return r.status_code == 201 and d.get("success") is True and d.get("data", {}).get("data_source") == "SIMULATED"


test("SIMULATED payload still accepted without change", test_simulated_still_works)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: Fault Condition via ESP32
# ─────────────────────────────────────────────────────────────────────────────
print("\n[ SECTION 4 ] Fault Conditions via ESP32 Data Source")

FAULT_CASES = [
    {"name": "High Pressure Fault", "payload": {"pressure": 6.80, "current": 7.10, "vibration": 2.90, "data_source": "ESP32"}},
    {"name": "Overcurrent Fault",   "payload": {"pressure": 3.50, "current": 9.90, "vibration": 3.30, "data_source": "ESP32"}},
    {"name": "High Vibration Fault","payload": {"pressure": 3.60, "current": 5.40, "vibration": 7.20, "data_source": "ESP32"}},
    {"name": "Combined Fault",      "payload": {"pressure": 1.40, "current": 8.50, "vibration": 7.60, "data_source": "ESP32"}},
]

for case in FAULT_CASES:
    def make_test(c):
        def _t():
            r = requests.post(f"{BASE_URL}/api/sensor-data", json=c["payload"], timeout=5)
            d = r.json()
            pred = d.get("data", {}).get("prediction", "N/A")
            src  = d.get("data", {}).get("data_source", "N/A")
            print(f"    prediction={pred} | data_source={src}")
            return r.status_code == 201 and d.get("success") is True and src == "ESP32"
        return _t
    test(f"ESP32 fault payload: {case['name']}", make_test(case))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: History API Shows Mixed Sources
# ─────────────────────────────────────────────────────────────────────────────
print("\n[ SECTION 5 ] History API - Mixed Data Source Verification")


def test_history_contains_esp32():
    r = requests.get(f"{BASE_URL}/api/history?limit=20", timeout=5)
    d = r.json()
    sources = [x.get("data_source") for x in d.get("data", [])]
    print(f"    sources in last 20: {list(set(sources))}")
    return "ESP32" in sources


test("GET /api/history contains ESP32 entries", test_history_contains_esp32)


def test_history_contains_simulated():
    r = requests.get(f"{BASE_URL}/api/history?limit=20", timeout=5)
    d = r.json()
    sources = [x.get("data_source") for x in d.get("data", [])]
    return "SIMULATED" in sources


test("GET /api/history still contains SIMULATED entries", test_history_contains_simulated)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6: Validation / Error Cases
# ─────────────────────────────────────────────────────────────────────────────
print("\n[ SECTION 6 ] Input Validation Edge Cases")


def test_missing_feature():
    r = requests.post(f"{BASE_URL}/api/sensor-data",
                      json={"pressure": 3.8, "current": 5.0},
                      timeout=5)
    d = r.json()
    print(f"    HTTP {r.status_code} | success={d.get('success')}")
    return r.status_code == 400 and d.get("success") is False


test("Missing vibration field -> 400 Bad Request", test_missing_feature)


def test_empty_json():
    r = requests.post(f"{BASE_URL}/api/sensor-data", json={}, timeout=5)
    print(f"    HTTP {r.status_code}")
    return r.status_code == 400


test("Empty JSON body -> 400 Bad Request", test_empty_json)


def test_non_json_body():
    r = requests.post(f"{BASE_URL}/api/sensor-data",
                      data="not json",
                      headers={"Content-Type": "text/plain"},
                      timeout=5)
    print(f"    HTTP {r.status_code}")
    return r.status_code == 400


test("Non-JSON Content-Type -> 400 Bad Request", test_non_json_body)

# ─────────────────────────────────────────────────────────────────────────────
# FINAL REPORT
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  PHASE 6 TEST RESULTS SUMMARY")
print("=" * 65)
total = PASSED + FAILED
print(f"  Total Tests : {total}")
print(f"  Passed      : {PASSED}")
print(f"  Failed      : {FAILED}")
print(f"  Pass Rate   : {PASSED/total*100:.1f}%")
print()
for name, status, msg in RESULTS:
    mark = "[PASS]" if status == "PASS" else "[FAIL]"
    extra = f" ({msg})" if msg else ""
    print(f"  {mark} {name}{extra}")
print("=" * 65)
print("  ESP32 HARDWARE INTEGRATION LAYER - VERIFICATION COMPLETE")
print("=" * 65)

if FAILED > 0:
    sys.exit(1)
