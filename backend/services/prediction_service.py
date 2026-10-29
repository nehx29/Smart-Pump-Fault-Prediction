import os
import json
import math
from datetime import datetime, timezone

import joblib
import numpy as np
import tensorflow as tf

from services.alert_service import evaluate_alert

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ML_MODEL_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'ml-model'))
SAVED_MODEL_DIR = os.path.join(ML_MODEL_DIR, 'saved_model')

MODEL_PATH = os.path.join(SAVED_MODEL_DIR, 'pump_fault_model.keras')
SCALER_PATH = os.path.join(SAVED_MODEL_DIR, 'scaler.pkl')
ENCODER_PATH = os.path.join(SAVED_MODEL_DIR, 'label_encoder.pkl')
CLASSES_PATH = os.path.join(SAVED_MODEL_DIR, 'classes.json')

FEATURE_ORDER = ['pressure', 'current', 'vibration']

_model = None
_scaler = None
_label_encoder = None
_classes_map = None
_model_loaded = False
_model_load_error = None


def load_ml_resources():
    """Load the existing trained model and original preprocessing artifacts once."""
    global _model, _scaler, _label_encoder, _classes_map, _model_loaded, _model_load_error

    if _model_loaded:
        return True, None

    try:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file missing: {MODEL_PATH}")
        if not os.path.exists(SCALER_PATH):
            raise FileNotFoundError(f"Scaler file missing: {SCALER_PATH}")
        if not os.path.exists(ENCODER_PATH):
            raise FileNotFoundError(f"Encoder file missing: {ENCODER_PATH}")
        if not os.path.exists(CLASSES_PATH):
            raise FileNotFoundError(f"Classes map missing: {CLASSES_PATH}")

        _model = tf.keras.models.load_model(MODEL_PATH)
        print("[OK] Trained model loaded")

        _scaler = joblib.load(SCALER_PATH)
        print("[OK] Original scaler loaded")

        _label_encoder = joblib.load(ENCODER_PATH)
        print("[OK] Label encoder loaded")

        with open(CLASSES_PATH, 'r') as f:
            _classes_map = json.load(f)
        print("[OK] Class mapping loaded")

        _model_loaded = True
        _model_load_error = None
        return True, None
    except Exception as e:
        _model_loaded = False
        _model_load_error = str(e)
        print(f"[ERROR] Failed to load ML resources: {e}")
        return False, str(e)


load_ml_resources()


def is_model_loaded():
    return _model_loaded


def _class_name_for_index(idx):
    """Map a model output index using the fitted LabelEncoder (existing class order)."""
    return str(_label_encoder.inverse_transform([int(idx)])[0])


def predict_pump_fault(pressure, current, vibration):
    """
    Validate inputs, apply the original scaler, run the existing trained model,
    and return the actual class and probabilities. Never fabricates a prediction.
    """
    if not _model_loaded or _model is None or _scaler is None or _label_encoder is None:
        success, err = load_ml_resources()
        if not success:
            return {
                "success": False,
                "error": f"Prediction service unavailable: {err}"
            }

    try:
        p = float(pressure)
        c = float(current)
        v = float(vibration)
    except (ValueError, TypeError):
        return {
            "success": False,
            "error": "Sensor inputs (pressure, current, vibration) must be valid numeric values."
        }

    if math.isnan(p) or math.isnan(c) or math.isnan(v):
        return {"success": False, "error": "Sensor inputs cannot be NaN."}

    if math.isinf(p) or math.isinf(c) or math.isinf(v):
        return {"success": False, "error": "Sensor inputs cannot be infinite."}

    try:
        raw_features = np.array([[p, c, v]], dtype=np.float64)
        scaled_features = _scaler.transform(raw_features)
        probs = np.asarray(_model.predict(scaled_features, verbose=0)[0], dtype=np.float64)

        if probs.ndim != 1 or len(probs) == 0:
            return {"success": False, "error": "Model returned an unexpected output shape."}

        predicted_idx = int(np.argmax(probs))
        predicted_class = _class_name_for_index(predicted_idx)
        confidence = float(probs[predicted_idx])

        probabilities_dict = {}
        for idx in range(len(probs)):
            probabilities_dict[_class_name_for_index(idx)] = float(probs[idx])

        alert_info = evaluate_alert(predicted_class, confidence)
        timestamp = datetime.now(timezone.utc).isoformat()

        return {
            "success": True,
            "prediction": predicted_class,
            "confidence": confidence,
            "probabilities": probabilities_dict,
            "input": {
                "pressure": p,
                "current": c,
                "vibration": v,
                "feature_order": FEATURE_ORDER,
            },
            "timestamp": timestamp,
            "explanation": alert_info["message"] if alert_info.get("is_fault") else None,
            "maintenance": alert_info["maintenance"] if alert_info.get("is_fault") else None,
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Prediction failed: {e}"
        }


def get_model_metadata():
    metrics_file = os.path.join(SAVED_MODEL_DIR, 'evaluation_metrics.json')
    metrics = None
    if os.path.exists(metrics_file):
        with open(metrics_file, 'r') as f:
            metrics = json.load(f)

    return {
        "input_features": FEATURE_ORDER,
        "target_classes": _classes_map,
        "is_model_loaded": _model_loaded,
        "load_error": _model_load_error,
        "evaluation_metrics": metrics
    }
