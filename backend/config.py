import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-pump-secret-key-2026')
    DATABASE_PATH = os.path.join(BASE_DIR, 'pump_monitoring.db')
    ML_MODEL_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'ml-model', 'saved_model'))
    CORS_HEADERS = 'Content-Type'
