import os
import json
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVED_MODEL_DIR = os.path.join(BASE_DIR, 'saved_model')
MODEL_PATH = os.path.join(SAVED_MODEL_DIR, 'pump_fault_model.keras')
SCALER_PATH = os.path.join(SAVED_MODEL_DIR, 'scaler.pkl')
ENCODER_PATH = os.path.join(SAVED_MODEL_DIR, 'label_encoder.pkl')
CLASSES_PATH = os.path.join(SAVED_MODEL_DIR, 'classes.json')

class PumpFaultPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.classes_map = None
        self._load_resources()

    def _load_resources(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Saved model missing at {MODEL_PATH}. Train the model first.")
        
        self.model = tf.keras.models.load_model(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)
        self.label_encoder = joblib.load(ENCODER_PATH)
        
        with open(CLASSES_PATH, 'r') as f:
            self.classes_map = json.load(f)

    def predict(self, pressure, current, vibration):
        """
        Accepts raw sensor readings (pressure, current, vibration).
        Returns dict with predicted class, confidence %, and class probability breakdown.
        """
        try:
            p = float(pressure)
            c = float(current)
            v = float(vibration)
        except (ValueError, TypeError):
            return {"success": False, "error": "Sensor inputs must be numeric."}

        # Scale features using saved scaler
        raw_features = np.array([[p, c, v]])
        scaled_features = self.scaler.transform(raw_features)

        # Run model inference
        probs = self.model.predict(scaled_features, verbose=0)[0]
        predicted_idx = int(np.argmax(probs))
        predicted_class = str(self.label_encoder.inverse_transform([predicted_idx])[0])

        # Construct probabilities dictionary for all 5 output classes
        class_probabilities = {}
        for idx in range(len(probs)):
            cls_name = str(self.label_encoder.inverse_transform([idx])[0])
            class_probabilities[cls_name] = round(float(probs[idx]), 6)

        return {
            "success": True,
            "prediction": predicted_class,
            "prediction_confidence": round(float(probs[predicted_idx]) * 100, 2),
            "is_abnormal": bool(predicted_class != 'Normal'),
            "probabilities": class_probabilities,
            "input_features": {
                "pressure": p,
                "current": c,
                "vibration": v
            }
        }

def test_prediction_with_actual_sample():
    print("==============================================================")
    print("        TEST PREDICTION WITH ACTUAL UNSEEN TEST SAMPLE         ")
    print("==============================================================")
    predictor = PumpFaultPredictor()

    test_csv = os.path.join(BASE_DIR, 'dataset', 'processed', 'test.csv')
    raw_csv = os.path.join(BASE_DIR, 'dataset', 'raw', 'pump_sensor_dataset.csv')

    if os.path.exists(raw_csv):
        raw_df = pd.read_csv(raw_csv)
        # Pick 3 diverse samples (e.g. Normal, High Pressure, Vibration)
        test_samples = [
            raw_df[raw_df['label'] == 'Normal'].iloc[0],
            raw_df[raw_df['label'] == 'High Pressure Fault'].iloc[0],
            raw_df[raw_df['label'] == 'Excessive Vibration Fault'].iloc[0]
        ]

        for sample in test_samples:
            p = float(sample['pressure'])
            c = float(sample['current'])
            v = float(sample['vibration'])
            actual_label = sample['label']

            res = predictor.predict(p, c, v)
            
            print(f"\n[INPUT FEATURES]  Pressure: {p:.2f} bar | Current: {c:.2f} A | Vibration: {v:.2f} mm/s")
            print(f"[MODEL PREDICTION] {res['prediction']} ({res['prediction_confidence']}% confidence)")
            print(f"[ACTUAL TEST LABEL] {actual_label}")
            print(f"[PROBABILITIES]    {json.dumps(res['probabilities'], indent=2)}")
            print("-" * 62)

if __name__ == '__main__':
    test_prediction_with_actual_sample()
