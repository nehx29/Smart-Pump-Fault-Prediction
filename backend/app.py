import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database import init_db

# Import Blueprints
from routes.health import health_bp
from routes.sensor import sensor_bp
from routes.prediction import prediction_bp
from routes.alerts import alerts_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # CORS configuration
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize SQLite Database inside app context
    with app.app_context():
        init_db()

    # Register API Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(sensor_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(alerts_bp)

    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            "service": "smart-pump-backend",
            "message": "Smart Pump Monitoring API. Use the documented /api routes.",
            "health": "/api/health",
            "endpoints": [
                "GET /api/health",
                "POST /api/predict",
                "POST /api/sensor-data",
                "GET /api/latest",
                "GET /api/history",
                "GET /api/alerts",
            ]
        }), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Endpoint not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"success": False, "error": "HTTP method not allowed for endpoint"}), 405

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "error": "Internal server error occurred"}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    # Listen on 0.0.0.0 so the Cloudflare Quick Tunnel can forward
    # external HTTPS requests arriving at 127.0.0.1:5000 to this process.
    # The React dev server proxy (vite.config.js) still uses 127.0.0.1:5000.
    print(f"[OK] Starting Smart Pump Monitoring Backend API Server")
    print(f"     Local access : http://127.0.0.1:{port}")
    print(f"     Tunnel access: bind 0.0.0.0:{port}  (Cloudflare forwards to 127.0.0.1:{port})")
    app.run(host='0.0.0.0', port=port, debug=False)
