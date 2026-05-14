# 🚀 AquaVision Quick Start

## Prerequisites
- Python 3.8+
- Virtual environment created
- Dependencies installed

## Step 1: Verify System
```bash
python verify.py
```

## Step 2: Setup Model
```bash
python setup_model.py
```

## Step 3: Run Server
```bash
python run.py
```

The server will start on `http://localhost:5000`

## Step 4: Configure ESP32 (Optional)

Edit `esp32/aqurium_final.ino`:
1. Change WiFi SSID and password
2. Set server IP to your laptop IP (shown in verify.py)
3. Upload to ESP32 using Arduino IDE

## Usage

### Web Dashboard
- Open `http://localhost:5000` in browser
- Navigate to different pages:
  - **Dashboard**: Real-time monitoring
  - **Analytics**: Historical data
  - **Media**: Processed images/videos
  - **Settings**: Alert thresholds

### API Commands

**Upload image for detection:**
```bash
curl -F "file=@image.jpg" http://localhost:5000/upload
```

**Get sensor data:**
```bash
curl http://localhost:5000/get-sensor
```

**Get fish count:**
```bash
curl http://localhost:5000/get-fish-data
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Model not found | Run `python setup_model.py` |
| Port 5000 in use | Change port in `run.py` |
| Camera error | Check camera connection |
| Import errors | Run `pip install -r requirements.txt` |

## Key Configuration Files

- **server/app.py**: Flask server and routes
- **server/ai_processor.py**: Fish detection logic
- **esp32/aqurium_final.ino**: ESP32 firmware
- **server/templates/index.html**: Web dashboard

---

**For detailed setup, see SETUP_GUIDE.md**
