from flask import Blueprint, request, jsonify
from services.sensor_service import process_and_store_sensor_data, fetch_latest_reading, fetch_sensor_history

sensor_bp = Blueprint('sensor', __name__)

@sensor_bp.route('/api/sensor-data', methods=['POST'])
def receive_sensor_data():
    if not request.is_json:
        return jsonify({"success": False, "error": "Content-Type must be application/json"}), 400
        
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({"success": False, "error": "Invalid or malformed JSON payload"}), 400

    if len(data) == 0:
        return jsonify({"success": False, "error": "Request body cannot be empty JSON"}), 400

    success, message, result = process_and_store_sensor_data(data)
    
    if not success:
        return jsonify({"success": False, "error": message}), 400

    return jsonify({
        "success": True,
        "message": message,
        "data": result
    }), 201

@sensor_bp.route('/api/latest', methods=['GET'])
def get_latest():
    reading = fetch_latest_reading()
    return jsonify({"success": True, "data": reading}), 200

@sensor_bp.route('/api/history', methods=['GET'])
def get_history():
    limit_arg = request.args.get('limit', default=20, type=int)
    limit = max(1, min(limit_arg, 500))
    
    readings = fetch_sensor_history(limit=limit)
    return jsonify({
        "success": True,
        "count": len(readings),
        "data": readings
    }), 200
