from flask import Flask, render_template, Response, request, jsonify, send_file
from werkzeug.utils import secure_filename
from flask_cors import CORS
from ai_processor import generate_frames, latest_data, process_uploaded_file
import logging
import sqlite3
from datetime import datetime, timedelta
from threading import Lock, Thread
import os
import random
import time

app = Flask(__name__)
CORS(app, origins=os.getenv('AQUAVISION_CORS_ORIGINS', 'http://localhost:5000').split(','))
logging.basicConfig(level=logging.INFO)

# Upload folder configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov', 'mkv'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

sensor_data = {
    "ph": 7.0,
    "temperature": 24.5,
    "turbidity": 2.5,
    "target_ph": 7.0,
    "timestamp": datetime.now().isoformat()
}

# Alert thresholds
ALERTS = {
    "target_ph": 7.0,
    "ph_min": 6.0,
    "ph_max": 8.0,
    "temp_min": 18,
    "temp_max": 28,
    "fish_threshold": 5
}

db_lock = Lock()

def init_db():
    """Initialize SQLite database for data persistence"""
    with db_lock:
        conn = sqlite3.connect('aqua_data.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS sensor_readings
                     (id INTEGER PRIMARY KEY, ph REAL, temperature REAL, 
                      turbidity REAL, target_ph REAL, timestamp TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS fish_detections
                     (id INTEGER PRIMARY KEY, count INTEGER, length_cm REAL, 
                      width_cm REAL, confidence REAL, timestamp TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS alerts
                     (id INTEGER PRIMARY KEY, type TEXT, message TEXT, timestamp TEXT)''')
        conn.commit()
        conn.close()

def log_sensor_data(data):
    """Store sensor data in database"""
    with db_lock:
        conn = sqlite3.connect('aqua_data.db')
        c = conn.cursor()
        c.execute('''INSERT INTO sensor_readings 
                     (ph, temperature, turbidity, target_ph, timestamp)
                     VALUES (?, ?, ?, ?, ?)''',
                  (data.get('ph', 0), data.get('temperature', 0),
                   data.get('turbidity', 0), data.get('target_ph', 0),
                   datetime.now().isoformat()))
        conn.commit()
        conn.close()

def log_alert(alert_type, message):
    """Store alerts in database"""
    with db_lock:
        conn = sqlite3.connect('aqua_data.db')
        c = conn.cursor()
        c.execute('''INSERT INTO alerts (type, message, timestamp)
                     VALUES (?, ?, ?)''',
                  (alert_type, message, datetime.now().isoformat()))
        conn.commit()
        conn.close()

def check_alerts(data):
    """Check if sensor data triggers any alerts"""
    alerts = []
    ph = data.get('ph', 0)
    temp = data.get('temperature', 0)
    
    if ph < ALERTS['ph_min']:
        msg = f"WARNING: pH too low ({ph})"
        alerts.append(msg)
        log_alert('pH', msg)
    elif ph > ALERTS['ph_max']:
        msg = f"WARNING: pH too high ({ph})"
        alerts.append(msg)
        log_alert('pH', msg)
    
    if temp < ALERTS['temp_min']:
        msg = f"WARNING: Temperature too low ({temp}°C)"
        alerts.append(msg)
        log_alert('temperature', msg)
    elif temp > ALERTS['temp_max']:
        msg = f"WARNING: Temperature too high ({temp}°C)"
        alerts.append(msg)
        log_alert('temperature', msg)
    
    return alerts

@app.route("/api/settings", methods=["GET", "POST"])
def settings_api():
    global ALERTS
    if request.method == "POST":
        try:
            data = request.json
            for key in ALERTS.keys():
                if key in data:
                    ALERTS[key] = float(data[key])
            return jsonify({"status": "success", "settings": ALERTS})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400
    return jsonify(ALERTS)

init_db()

USE_SIMULATED_DATA = True

# --- Simulation Thread for Dashboard ---
def simulate_dashboard_data():
    global sensor_data, USE_SIMULATED_DATA
    while True:
        if USE_SIMULATED_DATA:
            # Simulate sensor fluctuations
            sensor_data['temperature'] += random.uniform(-0.5, 0.5)
            sensor_data['temperature'] = max(18.0, min(28.0, sensor_data['temperature']))
            
            sensor_data['ph'] += random.uniform(-0.1, 0.1)
            sensor_data['ph'] = max(6.5, min(8.0, sensor_data['ph']))
            
            sensor_data['turbidity'] += random.uniform(-0.5, 0.5)
            sensor_data['turbidity'] = max(0.0, min(10.0, sensor_data['turbidity']))
            
            sensor_data['timestamp'] = datetime.now().isoformat()

            # Simulate fish detection count if camera isn't updating it
            if latest_data.get("count", 0) == 0 or random.random() < 0.3:
                latest_data["count"] = random.randint(2, 7)
                
            log_sensor_data(sensor_data)
            check_alerts(sensor_data)
        time.sleep(2)

sim_thread = Thread(target=simulate_dashboard_data, daemon=True)
sim_thread.start()
# ---------------------------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analytics")
def analytics():
    return render_template("analytics.html")

@app.route("/media")
def media():
    return render_template("media.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload_file():
    """Handle file upload and process for fish detection"""
    try:
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"status": "error", "message": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"status": "error", "message": "File type not allowed"}), 400
        
        # Save uploaded file
        import secrets
        safe_original_name = secure_filename(file.filename)
        if not safe_original_name:
            return jsonify({"status": "error", "message": "Invalid filename"}), 400
        filename = secrets.token_hex(8) + '_' + safe_original_name
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logging.info(f"File uploaded: {filename}")
        
        # Process file for detection
        file_type = filename.rsplit('.', 1)[1].lower()
        is_image = file_type in {'jpg', 'jpeg', 'png', 'gif'}
        is_video = file_type in {'mp4', 'avi', 'mov', 'mkv'}
        
        results = process_uploaded_file(filepath, is_image, is_video)
        
        return jsonify({
            "status": "success",
            "filename": filename,
            "file_type": "image" if is_image else "video",
            "results": results
        })
    
    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/result/<filename>")
def get_result(filename):
    """Get processed result image/video"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"result_{filename}")
        if os.path.exists(filepath):
            return send_file(filepath, mimetype='image/jpeg')
        else:
            return jsonify({"status": "error", "message": "Result not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/sensor-data", methods=["POST"])
@app.route("/api/sensors", methods=["POST"])
def receive_sensor_data():
    global sensor_data, USE_SIMULATED_DATA
    
    # Automatically switch off simulation if real hardware connects!
    USE_SIMULATED_DATA = False
    
    try:
        data = request.json
        if not data:
            return jsonify({"status":"error", "message":"No data provided"}), 400

        data["timestamp"] = datetime.now().isoformat()

        # Map ESP32 keys to internal keys (handle case differences)
        sensor_data = {
            "ph": data.get("pH", data.get("ph", 0)),  # Handle both "pH" and "ph"
            "temperature": data.get("temperature", 0),
            "turbidity": data.get("turbidity", 0),
            "target_ph": data.get("target_pH", data.get("target_ph", ALERTS["target_ph"])),
            "timestamp": data["timestamp"]
        }

        # Log to database
        log_sensor_data(sensor_data)

        # Check for alerts
        alerts = check_alerts(sensor_data)

        logging.info(f"Sensor data received: {sensor_data}")
        # Return target_pH so ESP32 can update if changed
        return jsonify({
            "status":"received",
            "alerts": alerts,
            "target_pH": ALERTS["target_ph"]
        })
    except Exception as e:
        logging.error(f"Error receiving sensor data: {e}")
        return jsonify({"status":"error", "message":str(e)}), 500

@app.route("/get-sensor")
def get_sensor():
    return jsonify(sensor_data)

@app.route("/get-fish-data")
def get_fish():
    return jsonify(latest_data)

@app.route("/get-alerts", methods=["GET"])
def get_alerts():
    """Get recent alerts from database"""
    with db_lock:
        conn = sqlite3.connect('aqua_data.db')
        c = conn.cursor()
        c.execute('''SELECT type, message, timestamp FROM alerts 
                     ORDER BY timestamp DESC LIMIT 10''')
        alerts = [{"type": row[0], "message": row[1], "timestamp": row[2]} for row in c.fetchall()]
        conn.close()
    return jsonify(alerts)

@app.route("/get-sensor-history", methods=["GET"])
def get_sensor_history():
    """Get sensor data from last N hours"""
    hours = request.args.get('hours', 1, type=int)
    with db_lock:
        conn = sqlite3.connect('aqua_data.db')
        c = conn.cursor()
        c.execute('''SELECT ph, temperature, turbidity, target_ph, timestamp 
                     FROM sensor_readings WHERE timestamp > datetime('now', '-' || ? || ' hours')
                     ORDER BY timestamp''', (hours,))
        readings = [{"ph": row[0], "temperature": row[1], "turbidity": row[2], 
                     "target_ph": row[3], "timestamp": row[4]} for row in c.fetchall()]
        conn.close()
    return jsonify(readings)

@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

if __name__ == "__main__":
    app.run(
        host=os.getenv('AQUAVISION_HOST', '0.0.0.0'),
        port=int(os.getenv('AQUAVISION_PORT', '5000')),
        debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    )