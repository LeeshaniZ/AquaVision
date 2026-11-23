import cv2
from ultralytics import YOLO
import math
from datetime import datetime
import os
import numpy as np

# Resolve the trained model relative to this file, not the process working directory.
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MODEL_PATH = os.path.join(SERVER_DIR, "best.pt")
MODEL_PATH = os.getenv("AQUAVISION_MODEL_PATH", DEFAULT_MODEL_PATH)

model = None
if os.path.isfile(MODEL_PATH):
    try:
        print(f"Loading AquaVision model from: {MODEL_PATH}")
        model = YOLO(MODEL_PATH)
    except Exception as exc:
        print(f"WARNING: Could not load configured model: {exc}")
else:
    print(
        "WARNING: AquaVision model not found. "
        "Fish detection is unavailable until server/best.pt is provided "
        "or AQUAVISION_MODEL_PATH points to a valid model."
    )

# A generic pretrained model is opt-in because its classes are not the
# project's goldfish dataset and should not be presented as AquaVision results.
if model is None and os.getenv("AQUAVISION_ALLOW_GENERIC_MODEL", "false").lower() == "true":
    try:
        model = YOLO("yolov8n.pt")
        print("WARNING: Using generic YOLOv8n; goldfish-specific detection is not validated.")
    except Exception as exc:
        print(f"WARNING: Could not load generic YOLOv8n model: {exc}")

# Initialize camera with error handling
cap = None
try:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("⚠️ WARNING: Camera not available. Video stream will not work.")
        cap = None
except Exception as e:
    print(f"⚠️ WARNING: Could not initialize camera: {e}")
    cap = None

# Calibration: Calculate pixels per cm based on tank width
TANK_WIDTH_CM = 40  # Adjust to your actual tank width
PIXEL_TO_CM = 0.05  # Fallback if calibration fails

latest_data = {
    "count": 0,
    "fish": [],
    "timestamp": datetime.now().isoformat()
}


def process_uploaded_file(filepath, is_image=True, is_video=False):
    """Process an uploaded image or video when a model is available."""
    if model is None:
        return {"status": "error", "message": "Fish detection model is unavailable. Configure AQUAVISION_MODEL_PATH."}

    try:
        if is_image:
            return process_image_file(filepath)
        elif is_video:
            return process_video_file(filepath)
    except Exception as e:
        print(f"Error processing file: {e}")
        return {"status": "error", "message": str(e)}


def process_image_file(filepath):
    """Process a single image file."""
    if model is None:
        return {"status": "error", "message": "Fish detection model is unavailable."}
    try:
        image = cv2.imread(filepath)
        if image is None:
            return {"status": "error", "message": "Could not read image"}
        
        image_width = image.shape[1]
        pixels_per_cm = image_width / TANK_WIDTH_CM
        
        results = model.predict(source=filepath, conf=0.5, verbose=False)
        detections = results[0].boxes
        
        fish_data = []
        
        for i, box in enumerate(detections):
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            length_px = max((x2 - x1), (y2 - y1))  # Longer dimension
            width_px = min((x2 - x1), (y2 - y1))   # Shorter dimension
            
            length_cm = length_px / pixels_per_cm
            width_cm = width_px / pixels_per_cm
            
            fish_data.append({
                "fish_num": i + 1,
                "length_cm": round(length_cm, 2),
                "width_cm": round(width_cm, 2),
                "confidence": round(conf, 2)
            })
            
            # Draw on image
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 200, 255), 2)
            label = f"Fish {i+1} | {length_cm:.1f}x{width_cm:.1f}cm | {conf:.2f}"
            cv2.putText(image, label, (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1)
        
        # Add total count
        cv2.putText(image, f"Total Fish: {len(detections)}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 100), 3)
        
        # Save result
        result_filename = f"result_{os.path.basename(filepath)}"
        result_path = os.path.join(os.path.dirname(filepath), result_filename)
        cv2.imwrite(result_path, image)
        
        return {
            "status": "success",
            "total_fish": len(detections),
            "fish_details": fish_data,
            "result_filename": f"result_{os.path.basename(filepath)}"
        }
    
    except Exception as e:
        print(f"Error processing image: {e}")
        return {"status": "error", "message": str(e)}


def process_video_file(filepath):
    """Process a video file for fish detection."""
    if model is None:
        return {"status": "error", "message": "Fish detection model is unavailable."}
    try:
        cap = cv2.VideoCapture(filepath)
        if not cap.isOpened():
            return {"status": "error", "message": "Could not open video"}
        
        image_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        pixels_per_cm = image_width / TANK_WIDTH_CM
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        result_filename = f"result_{os.path.basename(filepath)}"
        result_path = os.path.join(os.path.dirname(filepath), result_filename)
        out = cv2.VideoWriter(result_path, fourcc, fps, (image_width, int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
        
        frame_count = 0
        total_fish_detected = 0
        max_fish_in_frame = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            results = model.predict(source=frame, conf=0.5, verbose=False)
            detections = results[0].boxes
            
            total_fish_detected += len(detections)
            max_fish_in_frame = max(max_fish_in_frame, len(detections))
            
            for i, box in enumerate(detections):
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                length_px = max((x2 - x1), (y2 - y1))  # Longer dimension
                width_px = min((x2 - x1), (y2 - y1))   # Shorter dimension
                
                length_cm = length_px / pixels_per_cm
                width_cm = width_px / pixels_per_cm
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 255), 2)
                label = f"Fish {i+1} | {length_cm:.1f}x{width_cm:.1f}cm | {conf:.2f}"
                cv2.putText(frame, label, (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1)
            
            cv2.putText(frame, f"Fish in frame: {len(detections)}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 100), 3)
            
            out.write(frame)
        
        cap.release()
        out.release()
        
        return {
            "status": "success",
            "total_frames": frame_count,
            "max_fish_in_frame": max_fish_in_frame,
            "average_fish_per_frame": round(total_fish_detected / frame_count, 2) if frame_count > 0 else 0,
            "result_filename": f"result_{os.path.basename(filepath)}"
        }
    
    except Exception as e:
        print(f"Error processing video: {e}")
        return {"status": "error", "message": str(e)}


def generate_frames():
    global latest_data

    if model is None:
        print("Fish detection stream unavailable: no AquaVision model is loaded.")
        return

    if cap is None:
        print("⚠️ Camera not available")
        return

    while True:
        success, frame = cap.read()

        if not success:
            break

        results = model(frame)

        fish_data = []

        for result in results:
            boxes = result.boxes

            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Calculate fish dimensions
                box_width = x2 - x1
                box_height = y2 - y1

                # Length = longer dimension, Width = shorter dimension
                length_px = max(box_width, box_height)
                width_px = min(box_width, box_height)

                length_cm = round(length_px * PIXEL_TO_CM, 2)
                width_cm = round(width_px * PIXEL_TO_CM, 2)

                confidence = float(box.conf[0])

                fish_data.append({
                    "length_cm": length_cm,
                    "width_cm": width_cm,
                    "confidence": round(confidence, 2)
                })

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0,255,0),
                    2
                )

                label = f"Goldfish Length:{length_cm}cm Width:{width_cm}cm"

                cv2.putText(
                    frame,
                    label,
                    (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0,255,0),
                    2
                )

        latest_data = {
            "count": len(fish_data),
            "fish": fish_data,
            "timestamp": datetime.now().isoformat()
        }

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            frame_bytes +
            b'\r\n'
        )