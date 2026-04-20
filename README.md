# AquaVision - Smart Aquarium Monitoring System

## ✨ Features

### 1. **Real-Time Fish Detection**
- Live video feed using YOLO (You Only Look Once) object detection
- Automatically detects and measures goldfish
- Measures fish length and width in centimeters
- Displays confidence level for each detection

### 2. **Water Quality Monitoring**
- Real-time tracking of:
  - pH level
  - Water temperature
  - Turbidity (water clarity)
  - Target pH value
- Persistent data storage in SQLite database
- Historical data retrieval for trend analysis

### 3. **Alert System**
- Automatic alerts for:
  - **pH Level**: Warning if pH < 6.0 or > 8.0
  - **Temperature**: Warning if temp < 18°C or > 28°C
  - **Fish Anomalies**: Alert if unusual fish count detected
- All alerts logged to database with timestamps
- Real-time alert display on dashboard

### 4. **Data Visualization**
- Multi-axis chart showing:
  - pH trends (left axis)
  - Temperature trends (right axis)
  - Turbidity trends (far right axis)
- 1-hour historical data by default
- Real-time chart updates every 10 seconds

### 5. **Data Persistence**
- SQLite database with three tables:
  - `sensor_readings`: All sensor measurements with timestamps
  - `fish_detections`: Detected fish data with measurements
  - `alerts`: System alerts with types and messages
- Thread-safe database operations using locks

### 6. **Responsive Dashboard**
- Beautiful, modern UI with gradient background
- Mobile-responsive design
- Real-time updates via REST API
- Individual fish detail cards showing measurements

---

## 📁 Project Structure

```
AquaVision/
├── server/
│   ├── app.py                 # Flask backend with API endpoints
│   ├── ai_processor.py        # YOLO model processing
│   ├── templates/
│   │   └── index.html         # Dashboard UI
│   └── static/
│       ├── script.js          # Frontend JavaScript
│       └── style.css          # Dashboard styling
├── esp32/
│   └── aquarium_final.ino     # ESP32 sensor code
├── goldfish-detector.v4i.yolov8-obb/
│   └── best.pt                # Pre-trained YOLO model
└── requirements.txt           # Python dependencies
```

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- OpenCV
- YOLO model (best.pt)
- Flask & dependencies

### Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure YOLO model exists**:
   - Place `best.pt` in the same directory as `ai_processor.py`

3. **Configure alert thresholds** (optional):
   Edit `ALERTS` dictionary in `app.py`:
   ```python
   ALERTS = {
       "ph_min": 6.0,
       "ph_max": 8.0,
       "temp_min": 18,
       "temp_max": 28,
       "fish_threshold": 5
   }
   ```

### Running the Application

1. **Start the Flask server**:
   ```bash
   cd server
   python app.py
   ```

2. **Access the dashboard**:
   - Open browser to `http://localhost:5000`
   - Or from another machine: `http://<server-ip>:5000`

---

## 📡 API Endpoints

### GET Endpoints

| Endpoint | Description | Returns |
|----------|-------------|---------|
| `/` | Dashboard home page | HTML |
| `/video_feed` | Live MJPEG video stream | Video stream |
| `/get-sensor` | Current sensor readings | JSON |
| `/get-fish-data` | Latest fish detection data | JSON |
| `/get-alerts` | Recent alerts (limit 10) | JSON array |
| `/get-sensor-history?hours=N` | Sensor data from last N hours | JSON array |

### POST Endpoints

| Endpoint | Description | Body |
|----------|-------------|------|
| `/sensor-data` | Submit sensor readings from ESP32 | `{ph, temperature, turbidity, target_ph}` |

### Example POST Request

```bash
curl -X POST http://localhost:5000/sensor-data \
  -H "Content-Type: application/json" \
  -d '{
    "ph": 7.2,
    "temperature": 24.5,
    "turbidity": 2.1,
    "target_ph": 7.0
  }'
```

---

## 🗄️ Database Schema

### sensor_readings
```sql
CREATE TABLE sensor_readings (
    id INTEGER PRIMARY KEY,
    ph REAL,
    temperature REAL,
    turbidity REAL,
    target_ph REAL,
    timestamp TEXT
)
```

### fish_detections
```sql
CREATE TABLE fish_detections (
    id INTEGER PRIMARY KEY,
    count INTEGER,
    length_cm REAL,
    width_cm REAL,
    confidence REAL,
    timestamp TEXT
)
```

### alerts
```sql
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY,
    type TEXT,
    message TEXT,
    timestamp TEXT
)
```

---

## ⚙️ Configuration

### YOLO Model Calibration

Adjust pixel-to-centimeter ratio in `ai_processor.py`:
```python
PIXEL_TO_CM = 0.05  # Calibrate based on your camera setup
```

### Alert Thresholds

Edit `app.py` to customize when alerts trigger:
```python
ALERTS = {
    "ph_min": 6.0,      # Minimum pH
    "ph_max": 8.0,      # Maximum pH
    "temp_min": 18,     # Minimum temperature (°C)
    "temp_max": 28,     # Maximum temperature (°C)
    "fish_threshold": 5 # Alert if more than N fish detected
}
```

---

## 🐠 Features Explanation

### Real-Time Monitoring
- Dashboard updates every 2 seconds for sensor/fish data
- Chart updates every 10 seconds with new historical data
- Alerts check every 5 seconds

### Fish Measurement
- Uses bounding box dimensions from YOLO detection
- Converts pixel measurements to centimeters
- Displays length, width, and detection confidence

### Data Logging
- All sensor readings automatically stored
- Enables historical analysis and trend detection
- Thread-safe operations prevent database conflicts

---

## 🔧 Troubleshooting

### Flask server won't start
- Check if port 5000 is available
- Ensure all dependencies are installed
- Verify `best.pt` exists in the correct directory

### No video feed
- Check camera connection
- Verify OpenCV can access camera: `cv2.VideoCapture(0)`
- Try different camera index (0, 1, 2, etc.)

### Database errors
- Delete `aqua_data.db` to reset database
- Check file permissions in the server directory
- Ensure only one Flask instance is running

### Chart not displaying
- Verify Chart.js CDN is accessible
- Check browser console for JavaScript errors
- Ensure sensor-history endpoint returns data

---

## 📊 Example Sensor Data

```json
{
  "ph": 7.2,
  "temperature": 24.5,
  "turbidity": 2.1,
  "target_ph": 7.0,
  "timestamp": "2024-05-14T15:30:45.123456"
}
```

---

## 🔄 Update Intervals

| Component | Update Interval |
|-----------|-----------------|
| Sensor Data | 2 seconds |
| Fish Detection | 2 seconds |
| Alerts | 5 seconds |
| Chart Data | 10 seconds |

---

## 📝 Future Enhancements

- [ ] Mobile app for remote monitoring
- [ ] Email/SMS alerts
- [ ] Data export to CSV
- [ ] Machine learning for anomaly detection
- [ ] Water change reminders
- [ ] Fish species identification
- [ ] Integration with smart home systems

---

## 📄 License

MIT License - Free to use and modify

---

**Version**: 1.0.0  
**Last Updated**: May 14, 2024
