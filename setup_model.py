"""
Find and copy the trained best.pt model to the server directory
"""

import os
import shutil
from pathlib import Path

def find_best_pt():
    """Search for best.pt in common locations"""
    
    search_paths = [
        Path.cwd() / "best.pt",
        Path.cwd() / "runs" / "detect" / "train" / "weights" / "best.pt",
        Path.cwd() / "runs" / "detect" / "goldfish" / "weights" / "best.pt",
        Path.home() / "best.pt",
        Path.home() / "Downloads" / "best.pt",
        Path.home() / "Desktop" / "best.pt",
        Path.cwd() / "goldfish-detector.v4i.yolov8-obb" / "best.pt",
    ]
    
    print("🔍 Searching for best.pt model...")
    print("=" * 60)
    
    found_models = []
    
    for path in search_paths:
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"✅ FOUND: {path}")
            print(f"   Size: {size_mb:.1f} MB")
            found_models.append(path)
        else:
            print(f"❌ Not found: {path}")
    
    print("=" * 60)
    
    if not found_models:
        print("\n❌ No best.pt file found!")
        print("\nPlease provide the path to your model:")
        user_path = input("Enter full path to best.pt: ").strip()
        
        if user_path and Path(user_path).exists():
            return Path(user_path)
        else:
            print("❌ Invalid path!")
            return None
    
    if len(found_models) == 1:
        return found_models[0]
    else:
        print(f"\n🤔 Found {len(found_models)} models. Which one to use?")
        for i, model_path in enumerate(found_models, 1):
            print(f"{i}. {model_path}")
        
        choice = input("Enter number (1-{}): ".format(len(found_models)))
        try:
            return found_models[int(choice) - 1]
        except (ValueError, IndexError):
            return found_models[0]

def copy_model_to_server(source_path):
    """Copy model to server directory"""
    
    source = Path(source_path)
    dest = Path("server") / "best.pt"
    
    if not source.exists():
        print(f"❌ Source file not found: {source}")
        return False
    
    try:
        print(f"\n📋 Copying model...")
        print(f"   From: {source}")
        print(f"   To:   {dest}")
        
        shutil.copy2(source, dest)
        
        size_mb = dest.stat().st_size / (1024 * 1024)
        print(f"✅ SUCCESS! Model copied ({size_mb:.1f} MB)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error copying file: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🐠 AquaVision Model Setup")
    print("=" * 60 + "\n")
    
    # Find the model
    model_path = find_best_pt()
    
    if model_path:
        # Copy to server
        success = copy_model_to_server(model_path)
        
        if success:
            print("\n" + "=" * 60)
            print("✅ Setup complete! Your model is ready.")
            print("=" * 60)
            print("\n🚀 Next steps:")
            print("   1. cd server")
            print("   2. python app.py")
            print("   3. Open http://localhost:5000 in browser")
        else:
            print("\n❌ Setup failed!")
    else:
        print("\n❌ Could not find model!")
        print("\nManual steps:")
        print("1. Place your best.pt in: server/best.pt")
        print("2. Run: python app.py")
