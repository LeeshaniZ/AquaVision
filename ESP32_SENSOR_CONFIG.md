# 🐠 ESP32 SENSOR CONFIGURATION GUIDE

## Overview
The ESP32 collects sensor data and sends it to your Flask server every 10 seconds.

---

## 🔧 STEP 1: Configure Wi-Fi and Server

Never commit real Wi-Fi credentials or private network details to this repository.

1. In the `esp32` folder, copy `wifi_config.example.h` and rename the copy to `wifi_config.h`.
2. Open your local `wifi_config.h` and enter your own 2.4 GHz Wi-Fi network name, password, and Flask server URL.
3. Keep `wifi_config.h` local. It is excluded by the repository's `.gitignore` file.
4. If you change your router password, update the local configuration file and upload the firmware again.

Example configuration (use placeholders only in shared documentation):

```cpp
#define WIFI_SSID "YOUR_WIFI_NAME"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"
#define AQUAVISION_SERVER_URL "http://YOUR_LAPTOP_IP:5000/api/sensors"
```

To find your laptop's local IP address on Windows, run `ipconfig` and check the IPv4 address of the connected network adapter. Use that address in your local configuration file.

---

## 📌 STEP 2: Change Sensor Pins

Edit `esp32/aqurium_final.ino` (lines 16-21):

```cpp
// ========== Pin Definitions ==========
#define PH_PIN           1          // GPIO1 → pH sensor analog input
#define TURBIDITY_PIN    2          // GPIO2 → Turbidity analog input
#define DS18B20_PIN      4          // GPIO4 → Temperature sensor digital
#define VALVE_A_PIN      5          // GPIO5 → Acidic valve control (LOW/HIGH)
#define VALVE_B_PIN      6          // GPIO6 → Basic valve control (LOW/HIGH)
```

### Sensor Pin Details:

| Sensor | Pin | Type | Function |
|--------|-----|------|----------|
| **pH** | 1 | Analog Input | Reads voltage from pH probe |
| **Turbidity** | 2 | Analog Input | Reads voltage from turbidity sensor |
| **Temperature** | 4 | Digital | OneWire protocol (DS18B20) |
| **Valve A** | 5 | Digital Output | Opens when pH too LOW (needs pH up) |
| **Valve B** | 6 | Digital Output | Opens when pH too HIGH (needs pH down) |

### How to Change:
```cpp
// If your pH sensor is on GPIO 32 instead:
#define PH_PIN           32

// If your temperature sensor is on GPIO 14:
#define DS18B20_PIN      14

// If valves on GPIO 25 and 26:
#define VALVE_A_PIN      25
#define VALVE_B_PIN      26
```

---

## 🎯 STEP 3: Configure Sensor Behavior

Edit `esp32/aqurium_final.ino` (lines 24-27):

```cpp
// ========== pH Control Settings ==========
float targetPH = 7.0;                    // ← Target pH (default 7.0 for neutral)
const float pH_TOLERANCE = 0.1;          // ± tolerance range
const unsigned long VALVE_OPEN_MS = 5000;    // ← Time valve opens (5 seconds)
const unsigned long STABILISE_MS = 25000;    // ← Wait time for mixing (25 seconds)
```

### Adjust These Values:

**Target pH** (line 25):
```cpp
float targetPH = 6.5;  // For slightly acidic
float targetPH = 7.0;  // Neutral (default)
float targetPH = 7.5;  // Slightly basic
```

**pH Tolerance** (line 26) - Range allowed before adjustment:
```cpp
const float pH_TOLERANCE = 0.05;  // Very tight control (±0.05)
const float pH_TOLERANCE = 0.1;   // Standard control (±0.1) ← default
const float pH_TOLERANCE = 0.2;   // Loose control (±0.2)
```

**Valve Open Duration** (line 27) - How long to add chemicals:
```cpp
const unsigned long VALVE_OPEN_MS = 3000;   // 3 seconds (small dose)
const unsigned long VALVE_OPEN_MS = 5000;   // 5 seconds (medium dose) ← default
const unsigned long VALVE_OPEN_MS = 10000;  // 10 seconds (large dose)
```

**Stabilization Time** (line 28) - Wait time between adjustments:
```cpp
const unsigned long STABILISE_MS = 15000;  // 15 seconds (fast adjusting)
const unsigned long STABILISE_MS = 25000;  // 25 seconds (standard) ← default
const unsigned long STABILISE_MS = 60000;  // 60 seconds (slow adjusting)
```

---

## 📊 STEP 4: Calibrate Sensors

### pH Sensor Calibration:
```cpp
// In readSensors() function, line ~135:
float phVoltage = phRaw / 4095.0 * 3.3;  // Convert ADC to voltage
pH = ph.readPH(phVoltage, temp);         // DFRobot_PH library handles calibration
```

**To calibrate:**
1. Get pH 7.0 buffer solution
2. Dip sensor in solution
3. Note the voltage reading (Serial output)
4. Adjust DFRobot_PH calibration via Serial commands

### Turbidity Sensor Calibration:
```cpp
// In readSensors() function, line ~143:
int turbRaw = analogRead(TURBIDITY_PIN);
// Calibrate these values for your sensor (clear → 3500, dirty → 500)
turbidity = map(turbRaw, 500, 3500, 100, 0);  // ← Change these calibration values
turbidity = constrain(turbidity, 0, 100);
```

**Steps:**
1. Get clean water, note ADC reading
2. Get dirty/turbid water, note ADC reading
3. Update the map() function:
   ```cpp
   // If your sensor reads 4000 in clean, 100 in dirty:
   turbidity = map(turbRaw, 100, 4000, 100, 0);
   ```

### Temperature Sensor:
```cpp
// DS18B20 is auto-calibrated
// Just ensure proper wiring on GPIO4
sensors.requestTemperatures();
temp = sensors.getTempCByIndex(0);
```

---

## 📡 STEP 5: Upload to ESP32

### Using Arduino IDE:

1. **Install Board Support:**
   - Go to Tools → Board Manager
   - Search "ESP32"
   - Install "esp32 by Espressif Systems"

2. **Select Board:**
   - Tools → Board → ESP32 → (your ESP32 model)
   - Common: "ESP32 Dev Module"

3. **Install Libraries:**
   ```
   Sketch → Include Library → Manage Libraries
   - Search: "OneWire" → Install
   - Search: "DallasTemperature" → Install
   - Search: "DFRobot_PH" → Install
   - Search: "ArduinoJson" → Install
   ```

4. **Connect ESP32** via USB and select COM port

5. **Upload:**
   - Sketch → Upload (or Ctrl+U)

---

## 🧪 STEP 6: Test Connection

### Check Serial Monitor:
```
[BOOT] Aquarium Controller starting...
[EEPROM] Loaded target pH: 7.0
[WiFi] Connecting to YOUR_WIFI_NAME
[WiFi] Connected! IP: 192.168.1.50
pH:6.8  Temp:25.5  Turbidity:45
[HTTP] POST success → status 200
```

### Test with curl (from your laptop):
```bash
curl http://localhost:5000/get-sensor
```

You should see:
```json
{
  "ph": 6.8,
  "temperature": 25.5,
  "turbidity": 45,
  "target_ph": 7.0,
  "timestamp": "2026-05-14T10:30:45.123456"
}
```

---

## 🔄 STEP 7: Change Target pH from Web Dashboard

### Via Settings Page:
1. Open `http://localhost:5000`
2. Click **Tank Settings**
3. Adjust **Target pH** slider (6.0 - 10.0)
4. Click **Save**
5. ESP32 receives update next POST

### Via API (Advanced):
```bash
curl -X POST http://localhost:5000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"target_ph": 7.5}'
```

---

## 📝 SENSOR DATA FORMAT

ESP32 sends this every 10 seconds:
```json
{
  "pH": 6.8,
  "temperature": 25.5,
  "turbidity": 45,
  "target_pH": 7.0
}
```

Server responds:
```json
{
  "status": "received",
  "alerts": ["pH too low"],
  "target_pH": 7.0
}
```

---

## 🚨 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| **WiFi won't connect** | Check SSID/password spelling, WiFi 2.4GHz only |
| **Can't find server** | Update IP address in firmware, check firewall |
| **Sensor reads 0** | Check pin numbers match actual connections |
| **Temperature shows -999** | DS18B20 sensor disconnected |
| **Valve doesn't open** | Check GPIO pins have 5V relay connected |

---

## 📚 Complete Configuration Example

Create a local `esp32/wifi_config.h` file based on `esp32/wifi_config.example.h`. Keep real credentials in that local file only; do not commit it or share it in screenshots.

---

## 🎯 Summary

1. ✅ Configure local Wi-Fi credentials in the ignored `wifi_config.h` file
2. ✅ Update server IP (from `verify.py`)
3. ✅ Verify sensor pin assignments
4. ✅ Calibrate pH and turbidity sensors
5. ✅ Adjust control parameters
6. ✅ Upload to ESP32
7. ✅ Verify data in dashboard

**Data updates every 10 seconds!** 📡
