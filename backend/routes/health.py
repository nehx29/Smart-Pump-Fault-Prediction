from flask import Blueprint, jsonify
from services.prediction_service import is_model_loaded

health_bp = Blueprint('health', __name__)

@health_bp.route('/api/health', methods=['GET'])
def health_check():
    model_status = is_model_loaded()
    return jsonify({
        "status": "ok",
        "service": "smart-pump-backend",
        "model_loaded": model_status
    }), 200
