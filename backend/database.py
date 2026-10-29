import sqlite3
import os
from datetime import datetime, timezone
from config import Config


def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize SQLite and create sensor_readings if it does not exist."""
    os.makedirs(os.path.dirname(Config.DATABASE_PATH) or '.', exist_ok=True)
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                pressure REAL NOT NULL,
                current REAL NOT NULL,
                vibration REAL NOT NULL,
                data_source TEXT NOT NULL DEFAULT 'SIMULATED',
                prediction TEXT,
                confidence REAL
            )
        ''')
        conn.commit()
        print(f"[OK] SQLite database initialized at {Config.DATABASE_PATH}")
    finally:
        conn.close()


def insert_sensor_reading(pressure, current, vibration, data_source, prediction=None, confidence=None):
    """
    Insert a reading after prediction. Returns the stored row dict, or None on failure.
    Existing records are never deleted or overwritten.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            '''
            INSERT INTO sensor_readings (
                timestamp, pressure, current, vibration, data_source, prediction, confidence
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (timestamp, pressure, current, vibration, data_source, prediction, confidence)
        )
        reading_id = cursor.lastrowid
        conn.commit()
        cursor.execute('SELECT * FROM sensor_readings WHERE id = ?', (reading_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        if conn is not None:
            conn.rollback()
        print(f"[ERROR] Failed to insert sensor reading: {e}")
        return None
    finally:
        if conn is not None:
            conn.close()


def get_latest_reading():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sensor_readings ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_reading_history(limit=20):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sensor_readings ORDER BY id DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
