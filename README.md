# AquaVision — Smart Aquarium Monitoring System

AquaVision combines computer vision and IoT-based water-quality monitoring in a web dashboard for aquarium management. The project brings together an ESP32 sensor controller, a Flask application, and a YOLO-based goldfish detection pipeline.

## Project capabilities

- **Fish detection and measurement:** uses a YOLO model to detect goldfish and estimate length and width from image detections.
- **Water-quality monitoring:** reads pH, water temperature, and turbidity from connected sensors.
- **Dashboard and history:** provides a Flask-served web interface and stores monitoring records in SQLite.
- **pH control prototype:** includes ESP32 relay/valve control logic and a configurable target pH value.

> This is an academic/personal prototype. Sensor readings, measurement calibration, and automated dosing must be validated with the actual hardware before use in a live aquarium.

## Architecture

```text
ESP32 + sensors
    |
    | HTTP sensor readings
    v
Flask application  <--- camera / YOLO inference
    |
    +---- SQLite storage
    |
    v
Web dashboard
```

## Technology

| Area | Technologies |
|---|---|
| Backend | Python, Flask |
| Computer vision | Ultralytics YOLO, OpenCV |
| Data storage | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Embedded system | ESP32, Arduino C++ |
| Sensors | pH, turbidity, DS18B20 temperature |

## Repository structure

```text
AquaVision/
├── esp32/
│   ├── aqurium_final.ino
│   └── wifi_config.example.h
├── server/
│   ├── app.py
│   ├── ai_processor.py
│   ├── best.pt
│   ├── templates/
│   └── static/
├── requirements.txt
├── run.py
├── setup_model.py
└── train_model.py
```

## Run the web application

1. Install Python 3.10 or a version compatible with the pinned dependencies.
2. Create and activate a virtual environment.
3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the application using the repository's launcher:

   ```bash
   python run.py
   ```

5. Follow the startup output and open the local address shown by the application.

If you prefer to start the Flask app directly, review the configuration and startup requirements in `server/app.py` first.

## ESP32 configuration

Real Wi-Fi credentials and private network addresses must never be committed.

1. Copy `esp32/wifi_config.example.h` to `esp32/wifi_config.h`.
2. Set your local Wi-Fi name, password, and Flask server URL in `wifi_config.h`.
3. Keep `wifi_config.h` local; it is excluded by `.gitignore`.
4. Install the Arduino libraries used by the sketch and select the correct ESP32 board.
5. Upload the sketch to the ESP32.

The ESP32 and computer running Flask must be able to communicate over the same local network. Use a 2.4 GHz Wi-Fi network where required by your ESP32 board.

## Model

The repository includes a trained model file at `server/best.pt`. The detection pipeline is implemented in `server/ai_processor.py`. If you retrain or replace the model, document the dataset, training configuration, and evaluation metrics so results are reproducible.

## Safety and security

- Never commit Wi-Fi passwords, API keys, service-account files, or private network credentials.
- Rotate any credential that has previously been committed to a public repository.
- Removing a secret from the latest file does not remove it from Git history; historical secrets must also be purged.
- Test relay outputs and dosing logic safely before connecting valves to an aquarium. Automated pH adjustment can harm fish if sensors or calibration are incorrect.

## Sensor data modes

Sensor simulation is **disabled by default** so that example values are not mistaken for live hardware readings. To enable simulated dashboard data for a demonstration, set the environment variable before starting the app:

Windows PowerShell:

```powershell
$env:AQUAVISION_SIMULATED_DATA = "true"
python run.py
```

macOS / Linux:

```bash
AQUAVISION_SIMULATED_DATA=true python run.py
```

When simulation is disabled, the dashboard waits for readings from the ESP32. The `/api/status` endpoint reports whether the current readings are simulated, from hardware, or waiting for hardware.

## Server configuration

Optional environment variables:

- `AQUAVISION_MODEL_PATH`: path to the trained YOLO model (defaults to `server/best.pt`).
- `AQUAVISION_ALLOW_GENERIC_MODEL=true`: explicitly permits a generic YOLOv8n fallback. This is not a goldfish-trained model and must not be treated as validated AquaVision detection.
- `AQUAVISION_DATABASE_PATH`: custom SQLite database path.
- `AQUAVISION_SIMULATED_DATA=true`: enable simulated sensor readings for demonstration only.
- `AQUAVISION_HOST`, `AQUAVISION_PORT`, `FLASK_DEBUG`, `AQUAVISION_CORS_ORIGINS`: host, port, development debug mode, and allowed CORS origins.

## Current limitations

- Measurement accuracy depends on camera placement and pixel-to-centimetre calibration.
- Sensor accuracy depends on probe calibration and hardware condition.
- Hardware-specific pin assignments and network settings may need adjustment for a different ESP32 board or setup.
- This repository does not claim production-grade reliability or independently validated fish-health outcomes.

## Author

**Leeshani Dilthara** — Computer Science graduate

[GitHub profile](https://github.com/LeeshaniZ)
