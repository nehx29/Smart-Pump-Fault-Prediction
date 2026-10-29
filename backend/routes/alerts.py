"""
alerts.py — GET /api/alerts endpoint
Derives alerts from actual database records using the alert_service.
No fake or hardcoded alerts are generated.
"""
from flask import Blueprint, request, jsonify
from database import get_reading_history
from services.alert_service import get_alerts_from_history

alerts_bp = Blueprint('alerts', __name__)


@alerts_bp.route('/api/alerts', methods=['GET'])
def get_alerts():
    """
    Returns alert records derived from actual DNN predictions stored in the database.

    Query params:
        limit     : int  — max records to examine (default 50)
        faults_only : bool — if "true", returns only non-Normal predictions (default true)
    """
    limit_arg = request.args.get('limit', default=50, type=int)
    limit = max(1, min(limit_arg, 500))

    faults_only_arg = request.args.get('faults_only', default='true').strip().lower()
    faults_only = (faults_only_arg != 'false')

    readings = get_reading_history(limit=limit)
    all_alerts = get_alerts_from_history(readings)

    if faults_only:
        result = [a for a in all_alerts if a['is_fault']]
    else:
        result = all_alerts

    return jsonify({
        "success": True,
        "count": len(result),
        "faults_only": faults_only,
        "data": result
    }), 200
