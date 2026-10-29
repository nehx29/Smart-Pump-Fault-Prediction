from flask import Blueprint, request, jsonify
from services.prediction_service import predict_pump_fault, get_model_metadata

prediction_bp = Blueprint('prediction', __name__)


@prediction_bp.route('/api/predict', methods=['POST'])
def predict_endpoint():
    if not request.is_json:
        return jsonify({"success": False, "error": "Content-Type must be application/json"}), 400

    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({"success": False, "error": "Invalid or malformed JSON payload"}), 400

    if len(data) == 0:
        return jsonify({"success": False, "error": "Request body cannot be empty JSON"}), 400

    p = data.get('pressure')
    c = data.get('current')
    v = data.get('vibration')

    missing = []
    if p is None:
        missing.append('pressure')
    if c is None:
        missing.append('current')
    if v is None:
        missing.append('vibration')

    if missing:
        return jsonify({"success": False, "error": f"Missing required fields: {', '.join(missing)}"}), 400

    result = predict_pump_fault(p, c, v)
    if not result.get('success'):
        return jsonify({"success": False, "error": result.get('error', 'Prediction failed')}), 400

    return jsonify({
        "success": True,
        "prediction": result['prediction'],
        "confidence": result['confidence'],
        "probabilities": result['probabilities'],
        "input": result['input'],
        "timestamp": result.get('timestamp'),
        "explanation": result.get('explanation'),
    }), 200


@prediction_bp.route('/api/model-info', methods=['GET'])
def model_info_endpoint():
    metadata = get_model_metadata()
    return jsonify({
        "success": True,
        "data": metadata
    }), 200
