from database import insert_sensor_reading, get_latest_reading, get_reading_history
from services.prediction_service import predict_pump_fault
from services.alert_service import evaluate_alert

VALID_SOURCES = {
    'SIMULATED',
    'ESP32',
    'ESP32_LIVE',
    'WOKWI_SIMULATED',
    'TEST_READING',
}


def process_and_store_sensor_data(data):
    """
    Validate payload, run the existing trained model, then persist only after a
    successful database write.
    """
    if not isinstance(data, dict):
        return False, "Invalid JSON structure. Expected a JSON object.", None

    if len(data) == 0:
        return False, "Request body cannot be empty JSON.", None

    required_fields = ['pressure', 'current', 'vibration']
    missing = [f for f in required_fields if f not in data]
    if missing:
        return False, f"Missing required sensor field(s): {', '.join(missing)}", None

    pred_res = predict_pump_fault(data['pressure'], data['current'], data['vibration'])

    if not pred_res.get('success'):
        return False, pred_res.get('error', 'Prediction failed.'), None

    p = pred_res['input']['pressure']
    c = pred_res['input']['current']
    v = pred_res['input']['vibration']
    prediction = pred_res['prediction']
    confidence = pred_res['confidence']
    probabilities = pred_res['probabilities']

    data_source = str(data.get('data_source', 'SIMULATED')).strip().upper()
    if data_source not in VALID_SOURCES:
        data_source = 'SIMULATED'
        data_source = 'SIMULATED'

    saved_record = insert_sensor_reading(
        pressure=p,
        current=c,
        vibration=v,
        data_source=data_source,
        prediction=prediction,
        confidence=confidence
    )

    if not saved_record:
        return False, "Failed to store reading in the database.", None

    saved_record['probabilities'] = probabilities
    alert_info = evaluate_alert(prediction, confidence)
    saved_record['severity'] = alert_info['severity']
    saved_record['message'] = alert_info['message']
    saved_record['maintenance'] = alert_info['maintenance']
    saved_record['is_fault'] = alert_info['is_fault']
    saved_record['explanation'] = pred_res.get('explanation')

    return True, "Sensor reading processed and stored successfully.", saved_record


def fetch_latest_reading():
    return get_latest_reading()


def fetch_sensor_history(limit=20):
    return get_reading_history(limit=limit)
