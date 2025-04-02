import os
import time
import subprocess
import hashlib

# Configuration
BUILD_SCRIPT_PATH = os.path.join('src', 'build.py')
WATCH_INTERVAL = 1  # seconds
EXTENSIONS_TO_WATCH = ['.py', '.html', '.css', '.js', '.ipynb']

def get_file_hashes(directory='.', extensions=None):
    """Get hash of all files in directory with specified extensions"""
    file_hashes = {}
    for root, _, files in os.walk(directory):
        for file in files:
            # Skip hidden files and directories
            if file.startswith('.') or '/.git/' or './build/' in root:
                continue
                
            # Filter by extension if specified
            if extensions and not any(file.endswith(ext) for ext in extensions):
                continue
                
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                    file_hashes[filepath] = file_hash
            except (IOError, PermissionError):
                continue
    return file_hashes

def run_build():
    """Run the build.py script from the specified path"""
    print(f"\n⚙️ Running {BUILD_SCRIPT_PATH}...")
    try:
        subprocess.run(['python', BUILD_SCRIPT_PATH], check=True)
        print("✅ Build completed successfully\n")
    except subprocess.CalledProcessError:
        print("❌ Build failed\n")
    except FileNotFoundError:
        print(f"❌ Build script not found at {BUILD_SCRIPT_PATH}\n")

def watch_for_changes():
    # Initial build
    run_build()

    """Watch for file changes and run build.py when detected"""
    print(f"🔍 Watching for changes to files with extensions: {', '.join(EXTENSIONS_TO_WATCH)}")
    print(f"⏱️ Checking every {WATCH_INTERVAL} second(s)")
    print(f"🔧 Will run: {BUILD_SCRIPT_PATH}")
    print("📝 Press Ctrl+C to stop")
    
    
    # Get initial file hashes
    last_file_hashes = get_file_hashes(extensions=EXTENSIONS_TO_WATCH)
    
    try:
        while True:
            time.sleep(WATCH_INTERVAL)
            current_file_hashes = get_file_hashes(extensions=EXTENSIONS_TO_WATCH)
            
            # Check for changes
            if current_file_hashes != last_file_hashes:
                # Find changed files
                changed_files = []
                for file, hash_value in current_file_hashes.items():
                    if file not in last_file_hashes or last_file_hashes[file] != hash_value:
                        changed_files.append(file)
                
                for file in last_file_hashes:
                    if file not in current_file_hashes:
                        changed_files.append(f"{file} (deleted)")
                
                # Print changed files (limit to 5 to avoid clutter)
                if changed_files:
                    print(f"🔄 Changes detected in {len(changed_files)} file(s):")
                    for file in changed_files[:5]:
                        print(f"  - {file}")
                    if len(changed_files) > 5:
                        print(f"  - ...and {len(changed_files) - 5} more")
                    
                    # Run build
                    run_build()
                    
                # Update hashes
                last_file_hashes = current_file_hashes
    except KeyboardInterrupt:
        print("\n👋 File watcher stopped")

if __name__ == "__main__":
    watch_for_changes()