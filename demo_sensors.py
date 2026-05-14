#!/usr/bin/env python3
"""
Quick Sensor Data Test Script
Demonstrates how to change and test sensor data
"""

import requests
import time
import json

SERVER_URL = "http://localhost:5000"

def send_sensor_data(ph, temp, turbidity, target_ph=7.0):
    """Send sensor data to server"""
    data = {
        "pH": ph,
        "temperature": temp,
        "turbidity": turbidity,
        "target_pH": target_ph
    }

    try:
        response = requests.post(f"{SERVER_URL}/api/sensors", json=data)
        result = response.json()
        print(f"✅ Sent: pH={ph}, Temp={temp}°C, Turbidity={turbidity}%")
        if result.get("alerts"):
            print(f"⚠️  ALERTS: {', '.join(result['alerts'])}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def get_current_data():
    """Get current sensor data"""
    try:
        response = requests.get(f"{SERVER_URL}/get-sensor")
        data = response.json()
        print(f"📊 Current: pH={data.get('ph', 'N/A')}, Temp={data.get('temperature', 'N/A')}°C, Turbidity={data.get('turbidity', 'N/A')}%")
        return data
    except Exception as e:
        print(f"❌ Error getting data: {e}")
        return None

def change_target_ph(new_target):
    """Change target pH via settings API"""
    try:
        response = requests.post(f"{SERVER_URL}/api/settings",
                               json={"target_ph": new_target})
        result = response.json()
        print(f"🎯 Target pH changed to {new_target}")
        return True
    except Exception as e:
        print(f"❌ Error changing target: {e}")
        return False

def demo_normal_operation():
    """Demonstrate normal sensor operation"""
    print("\n" + "="*50)
    print("🟢 NORMAL OPERATION DEMO")
    print("="*50)

    print("\n📤 Sending normal sensor readings...")
    send_sensor_data(7.0, 25.0, 30)  # Normal values
    time.sleep(1)
    get_current_data()

def demo_ph_alert():
    """Demonstrate pH alert"""
    print("\n" + "="*50)
    print("⚠️  pH ALERT DEMO")
    print("="*50)

    print("\n📤 Sending low pH reading...")
    send_sensor_data(5.8, 25.0, 30)  # Low pH - should trigger alert
    time.sleep(1)
    get_current_data()

def demo_temperature_alert():
    """Demonstrate temperature alert"""
    print("\n" + "="*50)
    print("🔥 TEMPERATURE ALERT DEMO")
    print("="*50)

    print("\n📤 Sending high temperature reading...")
    send_sensor_data(7.0, 30.0, 30)  # High temp - should trigger alert
    time.sleep(1)
    get_current_data()

def demo_target_ph_change():
    """Demonstrate changing target pH"""
    print("\n" + "="*50)
    print("🎯 TARGET pH CHANGE DEMO")
    print("="*50)

    print("\n📤 Changing target pH to 7.5...")
    change_target_ph(7.5)

    print("\n📤 Sending pH reading that was normal before...")
    send_sensor_data(7.0, 25.0, 30)  # Now should trigger alert since target is 7.5
    time.sleep(1)
    get_current_data()

def demo_turbidity_alert():
    """Demonstrate turbidity alert"""
    print("\n" + "="*50)
    print("💨 TURBIDITY ALERT DEMO")
    print("="*50)

    print("\n📤 Sending high turbidity reading...")
    send_sensor_data(7.0, 25.0, 80)  # High turbidity
    time.sleep(1)
    get_current_data()

def main():
    """Run all demonstrations"""
    print("\n🐠 AQUAVISION SENSOR DATA DEMO")
    print("="*60)
    print("This script demonstrates how sensor data changes work")
    print("Make sure your server is running: python run.py")
    print("="*60)

    try:
        # Test connection first
        print("\n🔗 Testing server connection...")
        response = requests.get(f"{SERVER_URL}/get-sensor")
        if response.status_code == 200:
            print("✅ Server is running!")
        else:
            print("❌ Server not responding. Start with: python run.py")
            return

        # Run demonstrations
        demo_normal_operation()
        demo_ph_alert()
        demo_temperature_alert()
        demo_turbidity_alert()
        demo_target_ph_change()

        print("\n" + "="*60)
        print("🎉 DEMO COMPLETE!")
        print("="*60)
        print("\n📋 What you learned:")
        print("• How to send sensor data via API")
        print("• How alerts are triggered")
        print("• How to change target pH")
        print("• How data appears in dashboard")
        print("\n📚 For more details:")
        print("• ESP32_SENSOR_CONFIG.md - Hardware setup")
        print("• TEST_SENSOR_DATA.md - Testing methods")
        print("• SENSOR_QUICK_REF.md - Quick reference")

    except KeyboardInterrupt:
        print("\n\nDemo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("Make sure server is running: python run.py")

if __name__ == "__main__":
    main()
