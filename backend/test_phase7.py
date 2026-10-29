"""
=============================================================================
PHASE 7 - END-TO-END VALIDATION TEST SUITE
=============================================================================
Project      : Smart Pump Fault Prediction System
=============================================================================

Performs comprehensive end-to-end validation of the complete system:
  SIMULATED/ESP32 SENSOR DATA
        -> Flask REST API
        -> Input Validation
        -> Preprocessing (StandardScaler)
        -> Trained DNN Model
        -> Fault Classification
        -> Confidence Calculation
        -> Prediction Storage (SQLite)
        -> Alert Evaluation
        -> Dashboard / Alerts / History

All tests use actual model inference. No mocking of the DNN.
All sensor values are drawn from validated dataset ranges.

Physical hardware testing = PENDING (hardware not available).
=============================================================================
"""

import sys
import json
import requests

BASE = "http://127.0.0.1:5000"
PASSED, FAILED = 0, 0
RESULTS = []


# ─── Test helper ─────────────────────────────────────────────────────────────
def test(section, name, fn):
    global PASSED, FAILED
    try:
        ok, note = fn()
        status = "PASS" if ok else "FAIL"
        mark = "[PASS]" if ok else "[FAIL]"
        if ok:
            PASSED += 1
        else:
            FAILED += 1
        print(f"  {mark} {name}" + (f" -- {note}" if note else ""))
        RESULTS.append((section, name, status, note or ""))
    except Exception as exc:
        FAILED += 1
        print(f"  [ERROR] {name}: {exc}")
        RESULTS.append((section, name, "ERROR", str(exc)))


def post(payload):
    r = requests.post(f"{BASE}/api/sensor-data", json=payload,
                      headers={"Content-Type": "application/json"}, timeout=8)
    return r


def sep(title):
    print(f"\n[ {title} ]")


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1 - Backend & Model Health
# ═════════════════════════════════════════════════════════════════════════════
sep("SECTION 1 - Backend & Model Health")

def t_health_ok():
    r = requests.get(f"{BASE}/api/health", timeout=5)
    d = r.json()
    note = f"status={d.get('status')}"
    return r.status_code == 200 and d.get("status") == "ok", note

def t_model_loaded():
    r = requests.get(f"{BASE}/api/health", timeout=5)
    d = r.json()
    note = f"model_loaded={d.get('model_loaded')}"
    return d.get("model_loaded") is True, note

def t_model_info():
    r = requests.get(f"{BASE}/api/model-info", timeout=5)
    d = r.json()
    features = d.get("data", {}).get("input_features", [])
    note = f"features={features}"
    return set(features) == {"pressure", "current", "vibration"}, note

test("Health", "GET /api/health -> 200 and status=ok", t_health_ok)
test("Health", "DNN model is loaded (model_loaded=True)", t_model_loaded)
test("Health", "Model info: correct 3 input features", t_model_info)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Normal Condition
# ═════════════════════════════════════════════════════════════════════════════
sep("SECTION 2 — Normal Condition (SIMULATED)")

NORMAL_PAYLOAD = {"pressure": 3.73, "current": 4.79, "vibration": 0.96, "data_source": "SIMULATED"}
_normal_resp = {}

def t_normal_accepted():
    global _normal_resp
    r = post(NORMAL_PAYLOAD)
    _normal_resp = r.json()
    note = f"HTTP {r.status_code} | success={_normal_resp.get('success')}"
    return r.status_code == 201 and _normal_resp.get("success") is True, note

def t_normal_prediction():
    pred = _normal_resp.get("data", {}).get("prediction", "")
    note = f"prediction={pred}"
    return pred == "Normal", note

def t_normal_confidence():
    conf = _normal_resp.get("data", {}).get("confidence", -1)
    note = f"confidence={conf}"
    return isinstance(conf, float) and 0.0 <= conf <= 1.0, note

def t_normal_source():
    src = _normal_resp.get("data", {}).get("data_source", "")
    note = f"data_source={src}"
    return src == "SIMULATED", note

def t_normal_severity():
    sev = _normal_resp.get("data", {}).get("severity", "")
    note = f"severity={sev}"
    return sev == "NORMAL", note

def t_normal_maintenance():
    maint = _normal_resp.get("data", {}).get("maintenance", "")
    note = f"maintenance present={bool(maint)}"
    return len(maint) > 10, note

test("Normal", "POST /api/sensor-data Normal -> HTTP 201", t_normal_accepted)
test("Normal", "Normal: prediction class = 'Normal'", t_normal_prediction)
test("Normal", "Normal: confidence in [0.0, 1.0]", t_normal_confidence)
test("Normal", "Normal: data_source = SIMULATED", t_normal_source)
test("Normal", "Normal: alert severity = NORMAL", t_normal_severity)
test("Normal", "Normal: maintenance recommendation present", t_normal_maintenance)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3 — High Pressure Fault
# ═════════════════════════════════════════════════════════════════════════════
sep("SECTION 3 — High Pressure Fault (SIMULATED)")

HP_PAYLOAD = {"pressure": 6.31, "current": 6.69, "vibration": 2.61, "data_source": "SIMULATED"}
_hp_resp = {}

def t_hp_accepted():
    global _hp_resp
    r = post(HP_PAYLOAD)
    _hp_resp = r.json()
    note = f"HTTP {r.status_code}"
    return r.status_code == 201 and _hp_resp.get("success") is True, note

def t_hp_prediction():
    pred = _hp_resp.get("data", {}).get("prediction", "")
    note = f"prediction={pred}"
    return pred == "High Pressure Fault", note

def t_hp_severity():
    sev = _hp_resp.get("data", {}).get("severity", "")
    note = f"severity={sev}"
    return sev == "WARNING", note

def t_hp_confidence():
    conf = _hp_resp.get("data", {}).get("confidence", -1)
    note = f"confidence={conf}"
    return isinstance(conf, float) and 0.0 <= conf <= 1.0, note

test("HighPressure", "POST High Pressure Fault -> HTTP 201", t_hp_accepted)
test("HighPressure", "High Pressure Fault: prediction class correct", t_hp_prediction)
test("HighPressure", "High Pressure Fault: severity = WARNING", t_hp_severity)
test("HighPressure", "High Pressure Fault: confidence in [0, 1]", t_hp_confidence)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Excessive Vibration Fault
# ═════════════════════════════════════════════════════════════════════════════
sep("SECTION 4 — Excessive Vibration Fault (SIMULATED)")

VIB_PAYLOAD = {"pressure": 3.09, "current": 5.54, "vibration": 6.86, "data_source": "SIMULATED"}
_vib_resp = {}

def t_vib_accepted():
    global _vib_resp
    r = post(VIB_PAYLOAD)
    _vib_resp = r.json()
    note = f"HTTP {r.status_code}"
    return r.status_code == 201 and _vib_resp.get("success") is True, note

def t_vib_prediction():
    pred = _vib_resp.get("data", {}).get("prediction", "")
    note = f"prediction={pred}"
    return pred == "Excessive Vibration Fault", note

def t_vib_severity():
    sev = _vib_resp.get("data", {}).get("severity", "")
    note = f"severity={sev}"
    return sev == "WARNING", note

test("ExcessiveVibration", "POST Excessive Vibration Fault -> HTTP 201", t_vib_accepted)
test("ExcessiveVibration", "Excessive Vibration Fault: prediction class correct", t_vib_prediction)
test("ExcessiveVibration", "Excessive Vibration Fault: severity = WARNING", t_vib_severity)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Overcurrent Fault
# (validated range from simulator/dataset: current 8.8-11.2 A)
# ═════════════════════════════════════════════════════════════════════════════
sep("SECTION 5 — Overcurrent Fault (SIMULATED)")

OC_PAYLOAD = {"pressure": 3.50, "current": 9.90, "vibration": 3.30, "data_source": "SIMULATED"}
_oc_resp = {}

def t_oc_accepted():
    global _oc_resp
    r = post(OC_PAYLOAD)
    _oc_resp = r.json()
    note = f"HTTP {r.status_code}"
    return r.status_code == 201 and _oc_resp.get("success") is True, note

def t_oc_prediction():
    pred = _oc_resp.get("data", {}).get("prediction", "")
    note = f"prediction={pred}"
    return pred == "Overcurrent Fault", note

def t_oc_severity():
    sev = _oc_resp.get("data", {}).get("severity", "")
    note = f"severity={sev}"
    return sev == "WARNING", note

test("Overcurrent", "POST Overcurrent Fault -> HTTP 201", t_oc_accepted)
test("Overcurrent", "Overcurrent Fault: prediction class correct", t_oc_prediction)
test("Overcurrent", "Overcurrent Fault: severity = WARNING", t_oc_severity)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 6 — Combined Fault
# (validated range from simulator: pressure 1.0-2.2, current 7.5-9.8, vibration 6.0-9.2)
# ═════════════════════════════════════════════════════════════════════════════
sep("SECTION 6 — Combined Fault (SIMULATED)")

COMB_PAYLOAD = {"pressure": 1.40, "current": 8.50, "vibration": 7.60, "data_source": "SIMULATED"}
_comb_resp = {}

def t_comb_accepted():
    global _comb_resp
    r = post(COMB_PAYLOAD)
    _comb_resp = r.json()
    note = f"HTTP {r.status_code}"
    return r.status_code == 201 and _comb_resp.get("success") is True, note

def t_comb_prediction():
    pred = _comb_resp.get("data", {}).get("prediction", "")
    note = f"prediction={pred}"
    return pred == "Combined Fault", note

def t_comb_severity_critical():
    sev = _comb_resp.get("data", {}).get("severity", "")
    note = f"severity={sev}"
    return sev == "CRITICAL", note

def t_comb_is_fault():
    is_fault = _comb_resp.get("data", {}).get("is_fault", False)
    note = f"is_fault={is_fault}"
    return is_fault is True, note

test("CombinedFault", "POST Combined Fault -> HTTP 201", t_comb_accepted)
test("CombinedFault", "Combined Fault: prediction class correct", t_comb_prediction)
test("CombinedFault", "Combined Fault: severity = CRITICAL", t_comb_severity_critical)
test("CombinedFault", "Combined Fault: is_fault = True", t_comb_is_fault)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 7 — ESP32 API Compatibility
# Software/API compatibility test — not physical hardware
# ═════════════════════════════════════════════════════════════════════════════
sep("SECTION 7 — ESP32 API Compatibility (Software/API Test Only)")

ESP32_NORMAL = {"pressure": 3.73, "current": 4.79, "vibration": 0.96, "data_source": "ESP32"}
_esp32_resp = {}

def t_esp32_accepted():
    global _esp32_resp
    r = post(ESP32_NORMAL)
    _esp32_resp = r.json()
    note = f"HTTP {r.status_code} | success={_esp32_resp.get('success')}"
    return r.status_code == 201 and _esp32_resp.get("success") is True, note

def t_esp32_source():
    src = _esp32_resp.get("data", {}).get("data_source", "")
    note = f"data_source={src}"
    return src == "ESP32", note

def t_esp32_prediction():
    pred = _esp32_resp.get("data", {}).get("prediction", "")
    note = f"prediction={pred}"
    return isinstance(pred, str) and len(pred) > 0, note

def t_esp32_confidence():
    conf = _esp32_resp.get("data", {}).get("confidence", -1)
    note = f"confidence={conf}"
    return isinstance(conf, float) and 0.0 <= conf <= 1.0, note

def t_esp32_fault():
    r = post({"pressure": 6.80, "current": 7.10, "vibration": 2.90, "data_source": "ESP32"})
    d = r.json()
    pred = d.get("data", {}).get("prediction", "")
    src  = d.get("data", {}).get("data_source", "")
    note = f"prediction={pred}, source={src}"
    return src == "ESP32" and pred == "High Pressure Fault", note

test("ESP32", "ESP32 normal payload -> HTTP 201 (software test)", t_esp32_accepted)
test("ESP32", "ESP32: data_source=ESP32 stored correctly", t_esp32_source)
test("ESP32", "ESP32: DNN prediction returned", t_esp32_prediction)
test("ESP32", "ESP32: confidence in [0, 1]", t_esp32_confidence)
test("ESP32", "ESP32: fault payload correctly classified", t_esp32_fault)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 8 — Alert API
# ═════════════════════════════════════════════════════════════════════════════
sep("SECTION 8 — GET /api/alerts")

def t_alerts_ok():
    r = requests.get(f"{BASE}/api/alerts", timeout=5)
    d = r.json()
    note = f"HTTP {r.status_code} | success={d.get('success')} | count={d.get('count')}"
    return r.status_code == 200 and d.get("success") is True, note

def t_alerts_has_faults():
    r = requests.get(f"{BASE}/api/alerts?faults_only=true", timeout=5)
    d = r.json()
    alerts = d.get("data", [])
    has_fault = any(a.get("is_fault") is True for a in alerts)
    note = f"fault alerts={len(alerts)}, has_fault={has_fault}"
    return has_fault, note

def t_alerts_severity_present():
    r = requests.get(f"{BASE}/api/alerts?faults_only=true&limit=5", timeout=5)
    d = r.json()
    alerts = d.get("data", [])
    all_have_sev = all(a.get("severity") in ("WARNING", "CRITICAL", "NORMAL") for a in alerts)
    note = f"all have valid severity={all_have_sev}"
    return all_have_sev or len(alerts) == 0, note

def t_alerts_maintenance_present():
    r = requests.get(f"{BASE}/api/alerts?faults_only=true&limit=5", timeout=5)
    d = r.json()
    alerts = d.get("data", [])
    all_have_maint = all(len(a.get("maintenance", "")) > 5 for a in alerts)
    note = f"all have maintenance recommendation={all_have_maint}"
    return all_have_maint or len(alerts) == 0, note

def t_alerts_combined_is_critical():
    r = requests.get(f"{BASE}/api/alerts?faults_only=false&limit=100", timeout=5)
    d = r.json()
    combined = [a for a in d.get("data", []) if a.get("prediction") == "Combined Fault"]
    all_critical = all(a.get("severity") == "CRITICAL" for a in combined)
    note = f"combined alerts={len(combined)}, all CRITICAL={all_critical}"
    return all_critical or len(combined) == 0, note

test("Alerts", "GET /api/alerts -> 200 and success=True", t_alerts_ok)
test("Alerts", "GET /api/alerts: contains fault records", t_alerts_has_faults)
test("Alerts", "GET /api/alerts: severity field is valid", t_alerts_severity_present)
test("Alerts", "GET /api/alerts: maintenance recommendation present", t_alerts_maintenance_present)
test("Alerts", "GET /api/alerts: Combined Fault always CRITICAL", t_alerts_combined_is_critical)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 9 — History API & Database Validation
# ═════════════════════════════════════════════════════════════════════════════
sep("SECTION 9 — History API & Database Validation")

def t_history_ok():
    r = requests.get(f"{BASE}/api/history?limit=20", timeout=5)
    d = r.json()
    note = f"HTTP {r.status_code} | count={d.get('count')}"
    return r.status_code == 200 and d.get("success") is True, note

def t_history_has_data():
    r = requests.get(f"{BASE}/api/history?limit=20", timeout=5)
    d = r.json()
    count = d.get("count", 0)
    note = f"records={count}"
    return count > 0, note

def t_history_fields():
    r = requests.get(f"{BASE}/api/history?limit=5", timeout=5)
    d = r.json()
    required = {"id", "timestamp", "pressure", "current", "vibration", "prediction", "confidence", "data_source"}
    rows = d.get("data", [])
    if not rows:
        return True, "no rows yet"
    missing = required - set(rows[0].keys())
    note = f"missing fields={missing}"
    return len(missing) == 0, note

def t_history_mixed_sources():
    r = requests.get(f"{BASE}/api/history?limit=50", timeout=5)
    d = r.json()
    sources = {row.get("data_source") for row in d.get("data", [])}
    note = f"sources present={sources}"
    return "SIMULATED" in sources and "ESP32" in sources, note

def t_latest_ok():
    r = requests.get(f"{BASE}/api/latest", timeout=5)
    d = r.json()
    note = f"HTTP {r.status_code} | has_data={d.get('data') is not None}"
    return r.status_code == 200 and d.get("success") is True and d.get("data") is not None, note

test("History", "GET /api/history -> 200 and success=True", t_history_ok)
test("History", "GET /api/history: returns at least 1 record", t_history_has_data)
test("History", "GET /api/history: all required fields present", t_history_fields)
test("History", "GET /api/history: SIMULATED and ESP32 entries both present", t_history_mixed_sources)
test("History", "GET /api/latest -> 200 with valid data", t_latest_ok)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 10 — Prediction Endpoint
# ═════════════════════════════════════════════════════════════════════════════
sep("SECTION 10 — POST /api/predict (Manual Prediction)")

def t_predict_ok():
    r = requests.post(f"{BASE}/api/predict",
                      json={"pressure": 3.73, "current": 4.79, "vibration": 0.96},
                      timeout=8)
    d = r.json()
    note = f"HTTP {r.status_code} | success={d.get('success')} | prediction={d.get('prediction')}"
    return r.status_code == 200 and d.get("success") is True and "prediction" in d, note

def t_predict_probabilities():
    r = requests.post(f"{BASE}/api/predict",
                      json={"pressure": 3.73, "current": 4.79, "vibration": 0.96},
                      timeout=8)
    d = r.json()
    probs = d.get("probabilities", {})
    note = f"classes={list(probs.keys())}"
    return len(probs) == 5, note

def t_predict_missing_field():
    r = requests.post(f"{BASE}/api/predict",
                      json={"pressure": 3.73, "current": 4.79},
                      timeout=8)
    d = r.json()
    note = f"HTTP {r.status_code} | success={d.get('success')} | error={d.get('error')}"
    return r.status_code == 400 and d.get("success") is False, note

def t_predict_empty_body():
    r = requests.post(f"{BASE}/api/predict",
                      json={},
                      timeout=8)
    d = r.json()
    note = f"HTTP {r.status_code} | success={d.get('success')}"
    return r.status_code == 400 and d.get("success") is False, note

def t_predict_non_json():
    r = requests.post(f"{BASE}/api/predict",
                      data="not json",
                      headers={"Content-Type": "text/plain"},
                      timeout=8)
    note = f"HTTP {r.status_code}"
    return r.status_code == 400, note

def t_predict_confidence_range():
    r = requests.post(f"{BASE}/api/predict",
                      json={"pressure": 3.73, "current": 4.79, "vibration": 0.96},
                      timeout=8)
    d = r.json()
    conf = d.get("confidence", -1)
    note = f"confidence={conf}"
    return isinstance(conf, float) and 0.0 <= conf <= 1.0, note

test("Predict", "POST /api/predict returns 200 with success=True and prediction", t_predict_ok)
test("Predict", "POST /api/predict: 5-class probabilities returned", t_predict_probabilities)
test("Predict", "POST /api/predict: missing vibration field -> HTTP 400 success=False", t_predict_missing_field)
test("Predict", "POST /api/predict: empty body -> HTTP 400 success=False", t_predict_empty_body)
test("Predict", "POST /api/predict: non-JSON content -> HTTP 400", t_predict_non_json)
test("Predict", "POST /api/predict: confidence in [0.0, 1.0]", t_predict_confidence_range)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 11 — Input Validation & Error Handling
# ═════════════════════════════════════════════════════════════════════════════
sep("SECTION 11 — Input Validation & Error Handling")

def t_missing_pressure():
    r = post({"current": 5.0, "vibration": 1.2, "data_source": "SIMULATED"})
    note = f"HTTP {r.status_code}"
    return r.status_code == 400 and r.json().get("success") is False, note

def t_missing_vibration():
    r = post({"pressure": 3.8, "current": 5.0, "data_source": "SIMULATED"})
    note = f"HTTP {r.status_code}"
    return r.status_code == 400, note

def t_empty_body():
    r = post({})
    note = f"HTTP {r.status_code}"
    return r.status_code == 400, note

def t_non_json():
    r = requests.post(f"{BASE}/api/sensor-data", data="not json",
                      headers={"Content-Type": "text/plain"}, timeout=5)
    note = f"HTTP {r.status_code}"
    return r.status_code == 400, note

def t_nan_value():
    import json as _json
    import requests as _req
    # Send payload with NaN — Python requests does not natively support NaN in JSON
    # so we send it as raw string
    try:
        r = _req.post(
            f"{BASE}/api/sensor-data",
            data='{"pressure": NaN, "current": 5.0, "vibration": 1.0, "data_source": "SIMULATED"}',
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        # NaN is not valid JSON so Flask will reject at JSON parse level
        note = f"HTTP {r.status_code}"
        return r.status_code == 400, note
    except Exception as exc:
        return False, f"error: {exc}"

def t_invalid_source():
    r = post({"pressure": 3.8, "current": 5.0, "vibration": 1.2, "data_source": "HARDWARE_XYZ"})
    d = r.json()
    # Per sensor_service.py, invalid source falls back to SIMULATED — accepted with 201
    src = d.get("data", {}).get("data_source", "")
    note = f"HTTP {r.status_code}, source normalized to={src}"
    return r.status_code == 201 and src == "SIMULATED", note

test("Validation", "Missing 'pressure' field -> HTTP 400", t_missing_pressure)
test("Validation", "Missing 'vibration' field -> HTTP 400", t_missing_vibration)
test("Validation", "Empty JSON body -> HTTP 400", t_empty_body)
test("Validation", "Non-JSON Content-Type -> HTTP 400", t_non_json)
test("Validation", "NaN value -> rejected (HTTP 400)", t_nan_value)
test("Validation", "Invalid data_source -> normalized to SIMULATED (HTTP 201)", t_invalid_source)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 12 — Simulator Validation
# ═════════════════════════════════════════════════════════════════════════════
sep("SECTION 12 — Simulator Module Validation")

def t_simulator_import():
    import importlib.util, os
    spec = importlib.util.spec_from_file_location(
        "simulate_sensor",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "simulator", "simulate_sensor.py"))
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # Verify generate_sensor_values exists and produces valid output
    p, c, v = mod.generate_sensor_values("NORMAL")
    note = f"NORMAL sample: P={p}, C={c}, V={v}"
    return p > 0 and c > 0 and v > 0, note

def t_simulator_fault_mode():
    import importlib.util, os
    spec = importlib.util.spec_from_file_location(
        "simulate_sensor",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "simulator", "simulate_sensor.py"))
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    p, c, v = mod.generate_sensor_values("HIGH_VIBRATION")
    note = f"HIGH_VIBRATION sample: V={v} (expected > 5.0)"
    return v > 5.0, note

def t_simulator_send_once():
    # Use the simulator's send_reading function against the live backend
    import importlib.util, os
    spec = importlib.util.spec_from_file_location(
        "simulate_sensor",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "simulator", "simulate_sensor.py"))
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    res = mod.send_reading(3.80, 5.00, 1.20)
    note = f"response success={res and res.get('success')}"
    return res is not None and res.get("success") is True, note

test("Simulator", "Simulator module imports and generates NORMAL values", t_simulator_import)
test("Simulator", "Simulator HIGH_VIBRATION mode produces elevated vibration", t_simulator_fault_mode)
test("Simulator", "Simulator send_reading() calls live backend and gets prediction", t_simulator_send_once)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 13 — Full Pipeline Integration
# Sends all 5 fault classes end-to-end and verifies complete chain
# ═════════════════════════════════════════════════════════════════════════════
sep("SECTION 13 — Full Pipeline End-to-End Integration")

PIPELINE_CASES = [
    ("Normal",                    {"pressure": 3.80, "current": 5.00, "vibration": 1.20, "data_source": "SIMULATED"}),
    ("High Pressure Fault",       {"pressure": 6.31, "current": 6.69, "vibration": 2.61, "data_source": "SIMULATED"}),
    ("Excessive Vibration Fault", {"pressure": 3.09, "current": 5.54, "vibration": 6.86, "data_source": "SIMULATED"}),
    ("Overcurrent Fault",         {"pressure": 3.50, "current": 9.90, "vibration": 3.30, "data_source": "SIMULATED"}),
    ("Combined Fault",            {"pressure": 1.40, "current": 8.50, "vibration": 7.60, "data_source": "SIMULATED"}),
]

for expected_class, payload in PIPELINE_CASES:
    def make_pipeline_test(ec, pl):
        def _t():
            r = post(pl)
            d = r.json()
            data = d.get("data", {})
            pred  = data.get("prediction",  "")
            conf  = data.get("confidence",  -1)
            sev   = data.get("severity",    "")
            maint = data.get("maintenance", "")
            stored_ok = r.status_code == 201 and d.get("success") is True
            pred_ok   = pred == ec
            conf_ok   = isinstance(conf, float) and 0.0 <= conf <= 1.0
            sev_ok    = sev in ("NORMAL", "WARNING", "CRITICAL")
            maint_ok  = len(maint) > 10
            note = (f"pred={pred}, conf={round(conf,4)}, severity={sev}, "
                    f"stored={stored_ok}, maint={maint_ok}")
            return all([stored_ok, pred_ok, conf_ok, sev_ok, maint_ok]), note
        return _t
    test("Pipeline", f"Full pipeline: {expected_class}", make_pipeline_test(expected_class, payload))


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 14 — Not-Found / Method-Not-Allowed Error Handling
# ═════════════════════════════════════════════════════════════════════════════
sep("SECTION 14 — HTTP Error Handling")

def t_404():
    r = requests.get(f"{BASE}/api/does-not-exist", timeout=5)
    note = f"HTTP {r.status_code}"
    return r.status_code == 404, note

def t_405_get_on_post():
    r = requests.get(f"{BASE}/api/sensor-data", timeout=5)
    note = f"HTTP {r.status_code}"
    return r.status_code == 405, note

test("Errors", "GET /api/does-not-exist -> 404", t_404)
test("Errors", "GET /api/sensor-data (POST-only) -> 405", t_405_get_on_post)


# ═════════════════════════════════════════════════════════════════════════════
# FINAL REPORT
# ═════════════════════════════════════════════════════════════════════════════
total = PASSED + FAILED
print("\n" + "=" * 68)
print("  PHASE 7 TEST RESULTS SUMMARY")
print(f"  Smart Pump Fault Prediction System")
print("=" * 68)
print(f"  Total Tests : {total}")
print(f"  Passed      : {PASSED}")
print(f"  Failed      : {FAILED}")
print(f"  Pass Rate   : {PASSED/total*100:.1f}%")
print()

# Group by section
from collections import defaultdict
sections = defaultdict(list)
for section, name, status, note in RESULTS:
    sections[section].append((name, status, note))

for section, tests in sections.items():
    all_pass = all(s == "PASS" for _, s, _ in tests)
    indicator = "[OK]" if all_pass else "[!!]"
    print(f"  {indicator} {section}: {sum(1 for _,s,_ in tests if s=='PASS')}/{len(tests)} PASS")

print()
print("  HARDWARE STATUS: Physical ESP32 testing PENDING (hardware not available)")
print("  All ESP32 tests above are SOFTWARE/API compatibility only.")
print("=" * 68)

if FAILED > 0:
    print("\n  FAILING TESTS:")
    for section, name, status, note in RESULTS:
        if status != "PASS":
            print(f"    [{status}] [{section}] {name}")
            if note:
                print(f"           {note}")
    sys.exit(1)
else:
    print("\n  ALL PHASE 7 TESTS PASSED")
    print("=" * 68)
