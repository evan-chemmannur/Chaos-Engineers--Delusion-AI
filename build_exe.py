"""PyInstaller packaging script for LoveAI Windows executable."""

import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def build():
    print("==========================================")
    print("Building LoveAI Windows Desktop Executable")
    print("==========================================")
    
    icon_path = BASE_DIR / "assets" / "icon.ico"
    assets_dir = BASE_DIR / "assets"
    
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "LoveAI",
        f"--icon={icon_path}",
        f"--add-data={assets_dir};assets",
        "--collect-all", "customtkinter",
        "--collect-all", "cv2",
        "--collect-all", "PIL",
        "main.py"
    ]
    
    print(f"Running command:\n{' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=str(BASE_DIR))
    
    if result.returncode == 0:
        print("\n✓ Build completed successfully!")
        print(f"Executable output folder: {BASE_DIR / 'dist' / 'LoveAI' / 'LoveAI.exe'}")
    else:
        print("\n❌ Build failed with exit code:", result.returncode)
        sys.exit(result.returncode)

if __name__ == "__main__":
    build()
