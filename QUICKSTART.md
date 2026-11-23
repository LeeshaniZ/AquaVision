# AquaVision Quick Start

## Prerequisites

- Python 3.10 or a version compatible with the pinned packages
- Git
- An ESP32 board and supported sensors (optional for dashboard-only exploration)

## 1. Clone the repository

```bash
git clone https://github.com/LeeshaniZ/AquaVision.git
cd AquaVision
```

## 2. Create a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 4. Start the application

Run this command from the repository root:

```bash
python run.py
```

Open http://127.0.0.1:5000 in your browser. The first startup may take longer while computer-vision dependencies initialise.

The launcher expects the Flask application under `server/`. The project-trained model is stored at `server/best.pt`; if it is unavailable, the AI module may attempt to use the pretrained YOLOv8n model.

## 5. Configure the ESP32 (optional)

1. Copy `esp32/wifi_config.example.h` to `esp32/wifi_config.h`.
2. Add your own Wi-Fi SSID, password, and local Flask server URL.
3. Keep `wifi_config.h` private. It is excluded by `.gitignore`.
4. Open `esp32/aqurium_final.ino` in Arduino IDE, install the libraries referenced by the sketch, select your board, and upload.

The ESP32 and the computer running Flask must be able to communicate on the same network. Use your computer's local IPv4 address in the local configuration file.

## Useful API endpoints

| Purpose | Method and endpoint |
|---|---|
| Current sensor readings | `GET /get-sensor` |
| Latest fish detections | `GET /get-fish-data` |
| Sensor history | `GET /get-sensor-history` |
| Recent alerts | `GET /get-alerts` |
| Upload an image or video | `POST /upload` |

Example image upload:

```bash
curl -F "file=@image.jpg" http://127.0.0.1:5000/upload
```

## Configuration

The server accepts these optional environment variables:

- `AQUAVISION_HOST` (default: `0.0.0.0`)
- `AQUAVISION_PORT` (default: `5000`)
- `FLASK_DEBUG` (default: `false`)
- `AQUAVISION_CORS_ORIGINS` (default: `http://localhost:5000`)

Do not enable Flask debug mode on a network-accessible deployment.

## Troubleshooting

- **Missing dependency:** activate the virtual environment and run `python -m pip install -r requirements.txt`.
- **Camera unavailable:** check camera permissions and connection; the live camera stream will not be available without a camera.
- **Model unavailable:** confirm `server/best.pt` exists and review the model fallback message.
- **Port already in use:** set `AQUAVISION_PORT` to another available port before starting.
- **ESP32 cannot reach Flask:** check the local IP address, firewall rules, Wi-Fi network, and local `wifi_config.h`.

## Important

AquaVision is a prototype. Calibrate the sensors and camera-based size estimates, and test valve control safely before connecting the system to a live aquarium.
