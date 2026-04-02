
import os
import shutil

PROJECT_DIR = r"c:\Users\olato\OneDrive\Documents\Adechi website"
ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")

# Ensure target directories exist
TARGET_DIRS = {
    "js": os.path.join(ASSETS_DIR, "js"),
    "css": os.path.join(ASSETS_DIR, "css"),
    "fonts": os.path.join(ASSETS_DIR, "fonts"),
    "media": os.path.join(ASSETS_DIR, "media")
}

for d in TARGET_DIRS.values():
    os.makedirs(d, exist_ok=True)

EXTENSIONS = {
    ".js": "js",
    ".css": "css",
    ".woff2": "fonts", ".woff": "fonts", ".ttf": "fonts", ".otf": "fonts",
    ".jpg": "media", ".jpeg": "media", ".png": "media", ".gif": "media",
    ".svg": "media", ".mp4": "media", ".webp": "media", ".ico": "media"
}

def standardize():
    print("Standardizing assets...")
    # Walk through assets directory
    for root, dirs, files in os.walk(ASSETS_DIR):
        # Skip target directories to avoid moving files into themselves or infinite recursion
        if any(root.startswith(target) for target in TARGET_DIRS.values()):
            continue
            
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in EXTENSIONS:
                category = EXTENSIONS[ext]
                src_path = os.path.join(root, file)
                dest_dir = TARGET_DIRS[category]
                dest_path = os.path.join(dest_dir, file)
                
                # Check for collisions
                if os.path.exists(dest_path):
                    # If same file, skip. If different name, rename? 
                    # For now, append hash or suffix if needed.
                    # Actually, most shopify assets are already hashed.
                    if os.path.getsize(src_path) == os.path.getsize(dest_path):
                        print(f"Skipping duplicate: {file}")
                        # If it's not already in the target, we can delete the source to clean up
                        if src_path != dest_path:
                            try: os.remove(src_path)
                            except: pass
                        continue
                    else:
                        base, extension = os.path.splitext(file)
                        count = 1
                        while os.path.exists(dest_path):
                            dest_path = os.path.join(dest_dir, f"{base}_{count}{extension}")
                            count += 1
                
                print(f"Moving {file} to {category}/")
                try:
                    shutil.move(src_path, dest_path)
                except Exception as e:
                    print(f"Error moving {file}: {e}")

    # Remove empty directories in assets (except target ones)
    for root, dirs, files in os.walk(ASSETS_DIR, topdown=False):
        if root in TARGET_DIRS.values() or root == ASSETS_DIR:
            continue
        if not os.listdir(root):
            try:
                os.rmdir(root)
                print(f"Removed empty dir: {root}")
            except:
                pass

if __name__ == "__main__":
    standardize()
