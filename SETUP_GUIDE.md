# AquaVision 🐠 - Aquarium Management System

An intelligent aquarium monitoring system that combines AI-powered fish detection with real-time water quality sensors and automated pH control.

## Features

- **AI Fish Detection**: YOLOv8-based goldfish detection and sizing
- **Real-time Monitoring**: Live video feed with fish tracking
- **Water Quality Sensors**: pH, temperature, and turbidity monitoring
- **Automated pH Control**: Smart valve system for pH adjustment
- **Data Analytics**: Historical data tracking and alert system
- **Web Dashboard**: Real-time monitoring interface
- **ESP32 Integration**: IoT sensor data collection

## Project Structure

```
AquaVision/
├── server/               # Flask web server
│   ├── app.py           # Main Flask application
│   ├── ai_processor.py  # Fish detection logic
│   ├── best.pt          # Trained YOLOv8 model
│   ├── templates/       # HTML templates
│   ├── static/          # CSS/JS files
│   └── uploads/         # Processed images/videos
├── esp32/               # Arduino firmware
│   └── aqurium_final.ino
├── goldfish-detector.v4i.yolov8-obb/  # Training dataset
├── run.py              # Startup script
├── setup_model.py      # Model setup utility
├── train_model.py      # Model training script
└── requirements.txt    # Python dependencies
```

## Installation

### 1. Setup Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Model

The application needs a trained YOLOv8 model (`best.pt`):

**Option A: Use Existing Model**
```bash
python setup_model.py
```

**Option B: Train New Model**
```bash
# Make sure dataset exists at: goldfish-detector.v4i.yolov8-obb/
python train_model.py
```

### 3. Configure ESP32 (Optional)

Edit `esp32/aqurium_final.ino`:
- Set WiFi SSID and password
- Set server IP address (your laptop IP)
- Upload to ESP32 using Arduino IDE

## Running the Application

### Start the Server

```bash
# Option 1: Using startup script (recommended)
python run.py

# Option 2: Direct start
cd server
python app.py
```

Server runs on: `http://localhost:5000`

## API Endpoints

### Sensor Data
- **POST** `/api/sensors` - Receive sensor data from ESP32
- **GET** `/get-sensor` - Get latest sensor reading

### Fish Detection
- **GET** `/video_feed` - Live MJPEG stream
- **GET** `/get-fish-data` - Get latest fish count
- **POST** `/upload` - Upload image/video for detection
- **GET** `/result/<filename>` - Get processed result

### Analytics & Settings
- **GET** `/get-sensor-history` - Get historical data (hours parameter)
- **GET** `/get-alerts` - Get recent alerts
- **POST** `/api/settings` - Update alert thresholds
- **GET** `/api/settings` - Get current settings

### Web Pages
- `/` - Main dashboard
- `/analytics` - Historical data
- `/media` - Image/video gallery
- `/settings` - System settings

## Configuration

### Alert Thresholds

Update in `/api/settings` POST:
```json
{
  "target_ph": 7.0,
  "ph_min": 6.0,
  "ph_max": 8.0,
  "temp_min": 18,
  "temp_max": 28,
  "fish_threshold": 5
}
```

### Tank Calibration

Edit `server/ai_processor.py`:
```python
TANK_WIDTH_CM = 40  # Set to your actual tank width in cm
```

## ESP32 Sensor Connection

### Pin Configuration
- **pH Sensor**: GPIO1
- **Turbidity Sensor**: GPIO2
- **DS18B20 Temperature**: GPIO4
- **Valve A (Acidic)**: GPIO5
- **Valve B (Basic)**: GPIO6

### Network Setup
- WiFi credentials in `aqurium_final.ino`
- Server IP: Update to your laptop's IP address
- Data sent every 10 seconds to `/api/sensors`

## Troubleshooting

### Model Not Found
```
⚠️ WARNING: No trained model found
```
Solution: Run `python setup_model.py`

### Camera Not Available
```
⚠️ WARNING: Camera not available
```
Solution: Check webcam connection. Video stream will use pretrained model fallback.

### Server Connection Failed (ESP32)
- Check WiFi credentials
- Verify server IP address
- Ensure firewall allows port 5000

### Dependencies Missing
```bash
pip install -r requirements.txt
```

## Performance Tips

- **GPU Support**: Install CUDA-enabled PyTorch for faster inference
- **Camera Quality**: Use higher resolution for better fish detection
- **Tank Lighting**: Ensure adequate lighting for accurate detection
- **Model Size**: Use `yolov8n.pt` for speed, `yolov8m.pt` for accuracy

## Key Fixes Applied

✅ Fixed ESP32 API endpoint mismatch (`/api/sensors`)
✅ Added `target_pH` return in sensor response
✅ Fixed Windows/Linux path compatibility issues
✅ Added camera error handling
✅ Improved startup sequence
✅ Added database initialization on startup
✅ Added uploads directory auto-creation

## Future Enhancements

- [ ] Multiple camera support
- [ ] Advanced water quality parameters
- [ ] Machine learning-based alerts
- [ ] Mobile app interface
- [ ] Cloud data backup
- [ ] Email/SMS notifications

## License

MIT License - Feel free to use and modify

## Support

For issues and questions, check the troubleshooting section or review logs in `/server/aqua_data.db`

---

**Made with ❤️ for aquarium enthusiasts** 🐠
