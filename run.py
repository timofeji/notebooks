import os
import time
import subprocess
import hashlib

# Configuration
BUILD_SCRIPT_PATH = os.path.join('src', 'build.py')


def run_build():
    cmd = ['python', BUILD_SCRIPT_PATH]
    try:
        subprocess.run(cmd, check=True)
        print("✅ Build completed successfully\n")
    except subprocess.CalledProcessError:
        print("❌ Build failed\n")
    except FileNotFoundError:
        print(f"❌ Build script not found at {BUILD_SCRIPT_PATH}\n")

if __name__ == "__main__":
    run_build()