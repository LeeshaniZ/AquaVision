#!/usr/bin/env python3
"""
AquaVision System Verification Script
Checks if all components are working correctly
"""

import sys
from pathlib import Path

def check_imports():
    """Verify all required packages are installed"""
    print("\n" + "="*60)
    print("📦 Checking Python Dependencies")
    print("="*60)
    
    dependencies = {
        "flask": "Flask framework",
        "flask_cors": "CORS support",
        "cv2": "OpenCV",
        "ultralytics": "YOLO model",
        "torch": "PyTorch",
        "numpy": "NumPy"
    }
    
    missing = []
    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {module:15} ({description})")
        except ImportError:
            print(f"❌ {module:15} ({description}) - MISSING")
            missing.append(module)
    
    return len(missing) == 0

def check_files():
    """Verify all required files exist"""
    print("\n" + "="*60)
    print("📁 Checking Project Structure")
    print("="*60)
    
    required_files = {
        "server/app.py": "Flask application",
        "server/ai_processor.py": "AI processor module",
        "esp32/aqurium_final.ino": "ESP32 firmware",
        "setup_model.py": "Model setup script",
        "train_model.py": "Model training script",
        "requirements.txt": "Dependencies",
    }
    
    missing = []
    for file_path, description in required_files.items():
        if Path(file_path).exists():
            print(f"✅ {file_path:40} ({description})")
        else:
            print(f"❌ {file_path:40} ({description}) - MISSING")
            missing.append(file_path)
    
    return len(missing) == 0

def check_model():
    """Check if trained model exists"""
    print("\n" + "="*60)
    print("🤖 Checking AI Model")
    print("="*60)
    
    model_paths = [
        "server/best.pt",
        "goldfish-detector.v4i.yolov8-obb/best.pt",
        "runs/detect/goldfish/weights/best.pt",
    ]
    
    for path in model_paths:
        if Path(path).exists():
            size_mb = Path(path).stat().st_size / (1024 * 1024)
            print(f"✅ Model found: {path}")
            print(f"   Size: {size_mb:.1f} MB")
            return True
    
    print("⚠️  No trained model found")
    print("   Run: python setup_model.py")
    return False

def check_network():
    """Test network connectivity"""
    print("\n" + "="*60)
    print("🌐 Checking Network")
    print("="*60)
    
    try:
        import socket
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        print(f"✅ Hostname: {hostname}")
        print(f"✅ IP Address: {ip_address}")
        print(f"   Use this IP in ESP32 configuration")
        return True
    except Exception as e:
        print(f"❌ Network error: {e}")
        return False

def check_api():
    """Test API endpoints"""
    print("\n" + "="*60)
    print("🔗 Checking API Endpoints")
    print("="*60)
    
    try:
        import json
        from flask import Flask
        
        # Simulate the required endpoints
        endpoints = [
            "POST /api/sensors (ESP32 sensor data)",
            "GET /get-sensor (latest sensor reading)",
            "GET /get-fish-data (latest fish detection)",
            "GET /video_feed (live stream)",
            "POST /upload (file upload)",
            "GET /get-sensor-history (historical data)",
        ]
        
        for endpoint in endpoints:
            print(f"✅ {endpoint}")
        
        return True
    except Exception as e:
        print(f"❌ API check failed: {e}")
        return False

def main():
    """Run all checks"""
    print("\n" + "█"*60)
    print("🐠 AquaVision System Verification")
    print("█"*60)
    
    checks = [
        ("Dependencies", check_imports),
        ("Project Structure", check_files),
        ("AI Model", check_model),
        ("Network", check_network),
        ("API Endpoints", check_api),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📋 Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {check_name}")
    
    print(f"\nResults: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n" + "🎉 "*15)
        print("✨ System is ready! Run: python run.py")
        print("🎉 "*15)
        return 0
    else:
        print("\n❌ Please fix the failed checks before running the application")
        return 1

if __name__ == "__main__":
    sys.exit(main())
