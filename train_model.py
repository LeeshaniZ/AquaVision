"""
Train and export YOLO model for goldfish detection
This script handles model training, validation, and export
"""

import os
from ultralytics import YOLO
from pathlib import Path

def train_goldfish_model():
    """Train YOLO model on goldfish dataset"""
    
    print("🐠 Starting Goldfish Detection Model Training...")
    
    # Path to dataset
    dataset_path = "goldfish-detector.v4i.yolov8-obb/data.yaml"
    
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset not found at {dataset_path}")
        return False
    
    try:
        # Load a pretrained YOLOv8 model
        print("📦 Loading YOLOv8 model...")
        model = YOLO('yolov8m.pt')  # medium model for better accuracy
        
        # Train the model
        print("🚀 Training model on goldfish dataset...")
        print("This may take 30-60 minutes depending on your GPU...")
        
        results = model.train(
            data=dataset_path,
            epochs=100,
            imgsz=640,
            device=0,  # GPU device (0 for first GPU, -1 for CPU)
            patience=20,  # Early stopping
            save=True,
            project="runs/detect",
            name="goldfish",
            pretrained=True,
            optimizer='SGD',
            lr0=0.01,
            momentum=0.937,
            weight_decay=0.0005,
            warmup_epochs=3,
            warmup_momentum=0.8,
            box=7.5,
            cls=0.5,
            dfl=1.5,
            plots=True,
            exist_ok=False
        )
        
        print("✅ Training completed!")
        print(f"📊 Results saved in: {results.save_dir}")
        
        # Load the best trained model
        best_model_path = os.path.join(results.save_dir, "weights", "best.pt")
        if os.path.exists(best_model_path):
            print(f"✅ Best model found at: {best_model_path}")
            
            # Copy to server directory
            import shutil
            dest_path = "server/best.pt"
            shutil.copy(best_model_path, dest_path)
            print(f"✅ Model copied to: {dest_path}")
            
            return True
        else:
            print("❌ Best model not found")
            return False
            
    except Exception as e:
        print(f"❌ Error during training: {e}")
        return False

def export_to_pt():
    """Export existing trained model to .pt format"""
    
    print("📤 Exporting model to .pt format...")
    
    try:
        # Try to load from runs directory
        runs_path = Path("runs/detect/goldfish/weights/best.pt")
        
        if runs_path.exists():
            print(f"✅ Found trained model at: {runs_path}")
            
            # Load and save
            model = YOLO(str(runs_path))
            
            # Save to server directory
            dest_path = "server/best.pt"
            model.save(dest_path)
            print(f"✅ Model exported to: {dest_path}")
            
            # Also export to ONNX format (optional)
            print("📤 Exporting to ONNX format for faster inference...")
            model.export(format="onnx")
            print("✅ ONNX export complete")
            
            return True
        else:
            print(f"❌ Model not found at {runs_path}")
            print("Run training first with: python train_model.py train")
            return False
            
    except Exception as e:
        print(f"❌ Error during export: {e}")
        return False

def validate_model():
    """Validate the trained model"""
    
    print("🔍 Validating model...")
    
    try:
        model_path = "server/best.pt"
        
        if not os.path.exists(model_path):
            print(f"❌ Model not found at {model_path}")
            return False
        
        model = YOLO(model_path)
        
        # Validate on validation set
        results = model.val(data="goldfish-detector.v4i.yolov8-obb/data.yaml")
        
        print("✅ Validation complete!")
        print(f"📊 mAP50: {results.box.map50:.3f}")
        print(f"📊 mAP50-95: {results.box.map:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return False

def test_inference():
    """Test the model with inference"""
    
    print("🧪 Testing model inference...")
    
    try:
        model_path = "server/best.pt"
        
        if not os.path.exists(model_path):
            print(f"❌ Model not found at {model_path}")
            return False
        
        model = YOLO(model_path)
        
        # Test on a sample image from test set
        test_images = list(Path("goldfish-detector.v4i.yolov8-obb/test/images").glob("*.jpg"))[:3]
        
        if not test_images:
            print("⚠️ No test images found")
            return False
        
        print(f"Running inference on {len(test_images)} test images...")
        
        for img_path in test_images:
            results = model.predict(source=str(img_path), conf=0.25)
            print(f"✅ Detected {len(results[0].boxes)} objects in {img_path.name}")
        
        print("✅ Inference test complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error during inference test: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("🐠 Goldfish Detection Model Training & Export")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "train":
            success = train_goldfish_model()
            if success:
                print("\n" + "=" * 60)
                print("✅ Training pipeline complete!")
                print("Model saved to: server/best.pt")
                print("=" * 60)
        
        elif command == "export":
            success = export_to_pt()
            if success:
                print("\n✅ Export complete!")
        
        elif command == "validate":
            success = validate_model()
        
        elif command == "test":
            success = test_inference()
        
        elif command == "all":
            print("\n1️⃣ Exporting existing model...")
            export_to_pt()
            
            print("\n2️⃣ Validating model...")
            validate_model()
            
            print("\n3️⃣ Testing inference...")
            test_inference()
        
        else:
            print(f"❌ Unknown command: {command}")
            print("\nUsage:")
            print("  python train_model.py train     - Train model from scratch")
            print("  python train_model.py export    - Export trained model to .pt")
            print("  python train_model.py validate  - Validate model")
            print("  python train_model.py test      - Test inference")
            print("  python train_model.py all       - Export, validate, and test")
    
    else:
        print("\n📋 Available commands:")
        print("  python train_model.py train     - Train model from scratch")
        print("  python train_model.py export    - Export trained model to .pt")
        print("  python train_model.py validate  - Validate model")
        print("  python train_model.py test      - Test inference")
        print("  python train_model.py all       - Export, validate, and test")
        
        print("\n💡 Quick start:")
        print("  1. python train_model.py train    (Train new model)")
        print("  2. python train_model.py all      (Validate & test)")
        print("  3. python server/app.py           (Start dashboard)")
