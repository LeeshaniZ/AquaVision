#!/usr/bin/env python3
"""
AquaVision Startup Script
Initializes the application and starts the server
"""

import os
import sys
from pathlib import Path

def check_and_setup():
    """Check and setup all necessary directories and files"""
    
    print("\n" + "="*60)
    print("🐠 AquaVision Startup")
    print("="*60 + "\n")
    
    # Check if we're in the right directory
    required_dirs = ["server", "esp32", "goldfish-detector.v4i.yolov8-obb"]
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            print(f"❌ Missing directory: {dir_name}")
            print(f"Please run this script from the AquaVision root directory")
            return False
    
    # Create uploads directory if it doesn't exist
    uploads_dir = Path("server/uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Uploads directory: {uploads_dir}")
    
    # Check for model
    model_paths = [
        Path("server/best.pt"),
        Path("goldfish-detector.v4i.yolov8-obb/best.pt"),
        Path("runs/detect/goldfish/weights/best.pt"),
    ]
    
    model_found = False
    for path in model_paths:
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"✅ Model found: {path} ({size_mb:.1f} MB)")
            if path != model_paths[0]:  # If not in server, copy it
                import shutil
                shutil.copy2(path, model_paths[0])
                print(f"   Copied to: {model_paths[0]}")
            model_found = True
            break
    
    if not model_found:
        print(f"⚠️  WARNING: No trained model found!")
        print(f"   Expected: {model_paths[0]}")
        print(f"   Please run setup_model.py or place best.pt in server/")
        print(f"   Using pretrained YOLOv8n model as fallback")
    
    # Check requirements
    print("\n✅ Checking dependencies...")
    try:
        import flask
        import flask_cors
        import cv2
        import ultralytics
        import torch
        print("✅ All dependencies installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def start_server():
    """Start the Flask server"""
    
    print("\n" + "="*60)
    print("🚀 Starting AquaVision Server")
    print("="*60 + "\n")
    
    # Add server directory to Python path
    server_dir = os.path.join(os.getcwd(), "server")
    sys.path.insert(0, server_dir)
    
    # Change to server directory
    os.chdir("server")
    
    print("📡 Server starting on http://0.0.0.0:5000")
    print("   Open browser: http://localhost:5000")
    print("\n⚠️  Press Ctrl+C to stop\n")
    
    # Import and run Flask app
    try:
        from app import app
        app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        print("Trying alternative import method...")
        import importlib.util
        spec = importlib.util.spec_from_file_location("app", os.path.join(server_dir, "app.py"))
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        app_module.app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)

if __name__ == "__main__":
    try:
        if check_and_setup():
            start_server()
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n✋ Server stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
