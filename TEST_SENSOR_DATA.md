# 🧪 TEST SENSOR DATA WITHOUT ESP32

Use these methods to test your dashboard without physical sensors connected.

---

## METHOD 1: Test with curl (Recommended)

### Send Test Sensor Data:
```bash
curl -X POST http://localhost:5000/api/sensors \
  -H "Content-Type: application/json" \
  -d '{
    "pH": 7.2,
    "temperature": 24.5,
    "turbidity": 35,
    "target_pH": 7.0
  }'
```

### Get Current Sensor Data:
```bash
curl http://localhost:5000/get-sensor
```

### Get Fish Detection Data:
```bash
curl http://localhost:5000/get-fish-data
```

### Get Sensor History (last 24 hours):
```bash
curl http://localhost:5000/get-sensor-history?hours=24
```

### Get Alerts:
```bash
curl http://localhost:5000/get-alerts
```

---

## METHOD 2: Python Script to Simulate Data

Create file `test_sensors.py`:

```python
#!/usr/bin/env python3
"""
Test script to simulate sensor data
Run while server is running
"""

import requests
import time
import random
from datetime import datetime

SERVER_URL = "http://localhost:5000/api/sensors"

def send_sensor_data(ph, temp, turbidity):
    """Send sensor data to server"""
    data = {
        "pH": ph,
        "temperature": temp,
        "turbidity": turbidity,
        "target_pH": 7.0
    }
    
    try:
        response = requests.post(SERVER_URL, json=data)
        status = response.json()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] pH: {ph} | Temp: {temp}°C | Turbidity: {turbidity}%")
        print(f"  Response: {status}")
        
        if status.get("alerts"):
            print(f"  ⚠️  ALERTS: {', '.join(status['alerts'])}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_normal_conditions():
    """Test normal aquarium conditions"""
    print("\n📊 Testing Normal Conditions (10 seconds)...\n")
    
    for i in range(10):
        ph = 7.0 + random.uniform(-0.05, 0.05)  # ±0.05 around target
        temp = 25.0 + random.uniform(-0.5, 0.5)  # ±0.5°C around 25°C
        turbidity = 30 + random.randint(-5, 5)   # ±5% around 30%
        
        send_sensor_data(round(ph, 2), round(temp, 1), turbidity)
        time.sleep(1)

def test_low_ph():
    """Test low pH alert"""
    print("\n⚠️  Testing Low pH Alert...\n")
    
    for i in range(5):
        ph = 5.8  # Below minimum (6.0)
        temp = 25.0
        turbidity = 30
        
        send_sensor_data(ph, temp, turbidity)
        time.sleep(1)

def test_high_temp():
    """Test high temperature alert"""
    print("\n🔥 Testing High Temperature Alert...\n")
    
    for i in range(5):
        ph = 7.0
        temp = 29.5  # Above maximum (28°C)
        turbidity = 30
        
        send_sensor_data(ph, temp, turbidity)
        time.sleep(1)

def test_high_turbidity():
    """Test high turbidity"""
    print("\n💨 Testing High Turbidity...\n")
    
    for i in range(5):
        ph = 7.0
        temp = 25.0
        turbidity = 85  # High turbidity
        
        send_sensor_data(ph, temp, turbidity)
        time.sleep(1)

def test_all_scenarios():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 SENSOR TEST SUITE")
    print("="*60)
    
    test_normal_conditions()
    test_low_ph()
    test_high_temp()
    test_high_turbidity()
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)

if __name__ == "__main__":
    try:
        test_all_scenarios()
    except KeyboardInterrupt:
        print("\n\nTest stopped by user")
```

### Run the test:
```bash
python test_sensors.py
```

---

## METHOD 3: Manual Dashboard Update

You can also simulate data directly through the settings page:

1. Open `http://localhost:5000/settings`
2. Adjust alert thresholds:
   - pH Min/Max
   - Temperature Min/Max
   - Fish Detection Threshold
3. Click Save
4. Next sensor data will trigger alerts based on new thresholds

---

## METHOD 4: Database Direct Update (Advanced)

For testing, directly update the database:

```python
import sqlite3

conn = sqlite3.connect('server/aqua_data.db')
c = conn.cursor()

# Insert test sensor reading
c.execute('''INSERT INTO sensor_readings 
             (ph, temperature, turbidity, target_ph, timestamp)
             VALUES (?, ?, ?, ?, datetime('now'))''',
          (7.2, 24.5, 35, 7.0))

# Insert test alert
c.execute('''INSERT INTO alerts (type, message, timestamp)
             VALUES (?, ?, datetime('now'))''',
          ('pH', 'Test alert - pH adjustment needed'))

conn.commit()
conn.close()

print("✅ Test data inserted!")
```

---

## 📊 Expected Sensor Ranges

| Sensor | Min | Normal | Max | Alert Level |
|--------|-----|--------|-----|------------|
| **pH** | 6.0 | 7.0 | 8.0 | < 6.0 or > 8.0 |
| **Temp** | 18°C | 25°C | 28°C | < 18°C or > 28°C |
| **Turbidity** | 0% | 30% | 100% | > 50% (hazy) |

---

## 🔄 Continuous Sensor Simulation

For long-term testing, use this infinite loop:

```python
import requests
import time
import random

while True:
    ph = 6.8 + random.uniform(-0.3, 0.3)
    temp = 24 + random.uniform(-1, 1)
    turbidity = 25 + random.randint(-10, 10)
    
    data = {
        "pH": round(ph, 2),
        "temperature": round(temp, 1),
        "turbidity": max(0, min(100, turbidity))
    }
    
    try:
        response = requests.post("http://localhost:5000/api/sensors", json=data)
        print(f"✅ Sent: {data}")
    except:
        print(f"❌ Failed to send data")
    
    time.sleep(10)  # Send every 10 seconds like real ESP32
```

---

## ✅ Verification Checklist

After sending test data:

- [ ] Dashboard shows new values
- [ ] Alerts appear when thresholds exceeded
- [ ] Historical data populates
- [ ] Analytics page updates
- [ ] No errors in server console

---

## 🎯 Common Test Scenarios

### Scenario 1: Everything Normal ✅
```bash
curl -X POST http://localhost:5000/api/sensors -H "Content-Type: application/json" -d '{"pH": 7.0, "temperature": 25.0, "turbidity": 30}'
```

### Scenario 2: pH Too Low (trigger acidic valve) ⚠️
```bash
curl -X POST http://localhost:5000/api/sensors -H "Content-Type: application/json" -d '{"pH": 5.5, "temperature": 25.0, "turbidity": 30}'
```

### Scenario 3: Temperature Too High 🔥
```bash
curl -X POST http://localhost:5000/api/sensors -H "Content-Type: application/json" -d '{"pH": 7.0, "temperature": 30.0, "turbidity": 30}'
```

### Scenario 4: Very Turbid (cloudy) 💨
```bash
curl -X POST http://localhost:5000/api/sensors -H "Content-Type: application/json" -d '{"pH": 7.0, "temperature": 25.0, "turbidity": 80}'
```

---

## 📡 Check Server Response

Each POST should return:
```json
{
  "status": "received",
  "alerts": [],
  "target_pH": 7.0
}
```

If target_pH changed from settings, ESP32 will see the update on next poll!

---

**Now you can test all features without physical hardware!** 🎉
