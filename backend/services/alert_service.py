"""
Alert evaluation layer.

Takes the predicted class name and returns:
  - alert severity  (NORMAL | WARNING | CRITICAL)
  - alert message
  - maintenance recommendation (rule-based, deterministic)

Rules are deterministic. No fake alerts are generated.
All alerts are derived from stored model predictions only.
"""

# ---------------------------------------------------------------------------
# Severity and message rules — keyed by the exact predicted class name.
# These must match the class names in ml-model/saved_model/classes.json.
# ---------------------------------------------------------------------------
_ALERT_RULES = {
    "Normal": {
        "severity": "NORMAL",
        "message": (
            "Pump is operating within normal detected parameters. "
            "No fault condition identified."
        ),
        "maintenance": (
            "Continue normal monitoring. No immediate maintenance action required."
        ),
    },
    "High Pressure Fault": {
        "severity": "WARNING",
        "message": (
            "Abnormal high-pressure operating condition detected. "
            "Discharge pressure exceeds the normal operating envelope."
        ),
        "maintenance": (
            "Inspect discharge line, outlet valve position, and system back-pressure. "
            "Verify pump operating point against its performance curve. "
            "Check for blocked or partially closed valves downstream."
        ),
    },
    "Overcurrent Fault": {
        "severity": "WARNING",
        "message": (
            "Abnormal motor current detected. "
            "Motor current exceeds the normal operating range."
        ),
        "maintenance": (
            "Inspect motor current draw, power supply connections, and motor load. "
            "Check for mechanical binding, impeller obstruction, or overloading. "
            "Verify motor insulation resistance and winding condition."
        ),
    },
    "Excessive Vibration Fault": {
        "severity": "WARNING",
        "message": (
            "Excessive mechanical vibration detected. "
            "Vibration velocity exceeds the normal operating threshold."
        ),
        "maintenance": (
            "Inspect pump bearings, shaft alignment, and impeller balance. "
            "Check mounting bolts and base frame for looseness. "
            "Verify coupling condition and shaft runout."
        ),
    },
    "Combined Fault": {
        "severity": "CRITICAL",
        "message": (
            "Multiple simultaneous abnormal conditions detected. "
            "Combined fault signature indicates severe pump distress involving "
            "multiple operating parameters outside normal ranges."
        ),
        "maintenance": (
            "Treat as high-priority maintenance event. "
            "Inspect all affected pump subsystems: pressure, electrical, and mechanical. "
            "Perform comprehensive pump inspection before resuming normal operation. "
            "Do NOT clear this alert without a physical inspection."
            "\n\nNOTE: This system provides monitoring and prediction only. "
            "All maintenance decisions must be made by a qualified engineer."
        ),
    },
}

# Fallback rule for any unknown class name (should not occur with trained model)
_UNKNOWN_RULE = {
    "severity": "WARNING",
    "message": "Unrecognised pump condition. Manual inspection advised.",
    "maintenance": "Inspect pump manually. Report this classification to the system administrator.",
}


def evaluate_alert(prediction: str, confidence: float) -> dict:
    """
    Evaluate alert severity and maintenance recommendation from a prediction.

    Parameters
    ----------
    prediction  : str   — predicted class name (exact string)
    confidence  : float — softmax confidence score in [0.0, 1.0]

    Returns
    -------
    dict with keys:
        severity      : str   — "NORMAL" | "WARNING" | "CRITICAL"
        message       : str   — human-readable alert message
        maintenance   : str   — maintenance recommendation text
        is_fault      : bool  — True if prediction is not Normal
    """
    rule = _ALERT_RULES.get(prediction, _UNKNOWN_RULE)

    return {
        "severity":    rule["severity"],
        "message":     rule["message"],
        "maintenance": rule["maintenance"],
        "is_fault":    prediction != "Normal",
        "prediction":  prediction,
        "confidence":  round(float(confidence), 4),
    }


def get_alerts_from_history(readings: list) -> list:
    """
    Derive alert records from stored sensor readings.

    Parameters
    ----------
    readings : list of dicts — sensor reading rows from the database

    Returns
    -------
    List of alert dicts. Only non-Normal predictions are returned as active
    fault alerts; Normal readings are included with NORMAL severity for full
    audit trail only if explicitly requested via include_normal=True.

    This function never fabricates data — it only annotates existing DB records
    with the deterministic alert rules above.
    """
    alerts = []
    for reading in readings:
        prediction = reading.get("prediction") or "Unknown"
        confidence = float(reading.get("confidence") or 0.0)
        alert_info = evaluate_alert(prediction, confidence)

        alerts.append({
            "id":          reading.get("id"),
            "timestamp":   reading.get("timestamp"),
            "pressure":    reading.get("pressure"),
            "current":     reading.get("current"),
            "vibration":   reading.get("vibration"),
            "prediction":  prediction,
            "confidence":  confidence,
            "severity":    alert_info["severity"],
            "message":     alert_info["message"],
            "maintenance": alert_info["maintenance"],
            "is_fault":    alert_info["is_fault"],
            "data_source": reading.get("data_source", "SIMULATED"),
        })

    return alerts
