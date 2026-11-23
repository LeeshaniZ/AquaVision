#!/usr/bin/env python3
"""Start the AquaVision Flask application from the repository root."""

import os
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
SERVER_DIR = ROOT_DIR / "server"
MODEL_PATH = SERVER_DIR / "best.pt"


def check_and_setup():
    """Validate the files needed to start the application."""
    print("\n" + "=" * 60)
    print("AquaVision startup")
    print("=" * 60)

    if not SERVER_DIR.is_dir():
        print(f"Missing application directory: {SERVER_DIR}")
        return False

    (SERVER_DIR / "uploads").mkdir(parents=True, exist_ok=True)

    if MODEL_PATH.is_file():
        print(f"Trained model found: {MODEL_PATH}")
    else:
        print("No project-trained model found in server/best.pt.")
        print("The AI module may fall back to the pretrained YOLOv8n model.")

    try:
        import flask  # noqa: F401
        import flask_cors  # noqa: F401
        import cv2  # noqa: F401
        import ultralytics  # noqa: F401
        import torch  # noqa: F401
    except ImportError as exc:
        print(f"Missing dependency: {exc}")
        print("Install dependencies with: pip install -r requirements.txt")
        return False

    return True


def start_server():
    """Import and run Flask without enabling the development debugger."""
    sys.path.insert(0, str(SERVER_DIR))
    os.chdir(SERVER_DIR)

    from app import app

    host = os.getenv("AQUAVISION_HOST", "0.0.0.0")
    port = int(os.getenv("AQUAVISION_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    print(f"Starting AquaVision at http://127.0.0.1:{port}")
    app.run(host=host, port=port, debug=debug, use_reloader=False)


if __name__ == "__main__":
    try:
        if check_and_setup():
            start_server()
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nAquaVision stopped.")
        sys.exit(0)
