
import os

PROJECT_DIR = r"c:\Users\olato\OneDrive\Documents\Adechi website"
MEDIA_DIR_REL = "assets/media"

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fixed basePath
    # Pattern: const basePath = '...';
    # distinct from the import map
    
    new_content = content.replace("const basePath = 'https://cdn.shopify.com/static/themes/horizon/placeholders';", "const basePath = '.';")
    
    # Fix Import Map
    # The import map has lines like: "@theme/critical": "//greedyunit.com/cdn/shop/t/12/assets/critical.js?v=..."
    # We want to replace "//greedyunit.com/cdn/shop/t/12/assets/" with relative path to assets/media/
    
    rel_path_from_root = os.path.relpath(file_path, PROJECT_DIR)
    depth = len(rel_path_from_root.split(os.sep)) - 1
    
    media_prefix = "./" + MEDIA_DIR_REL + "/"
    if depth > 0:
        media_prefix = "../" * depth + MEDIA_DIR_REL + "/"
    
    # Common prefix for assets in import map seems to be: //greedyunit.com/cdn/shop/t/12/assets/
    # We can try to replace that.
    # Also need to handle just //greedyunit.com/cdn/shop/t/12/assets/ (with version params)
    
    # Naive replacement of the prefix
    remote_prefix = "//greedyunit.com/cdn/shop/t/12/assets/"
    if remote_prefix in new_content:
        print(f"Fixing import map in {file_path}")
        new_content = new_content.replace(remote_prefix, media_prefix)
    
    # Remove query params from the import map URLs if they were downloaded without them?
    # correct, download_all_media.py saved them as 'filename.js'.
    # But the import map text has 'filename.js?v=...'
    # My simple replacement above leaves '?v=...'.
    # Local file system ignores query params? No, file system paths cannot have '?'.
    # References in HTML/JS: src="file.js?v=1" -> Browser treats ?v=1 as query param even for local files (sometimes).
    # But `download_all_media.py` updated the `script src` tags to *remove* the query param in the filename it wrote?
    # Let's check `download_all_media.py`: 
    # `filename = get_filename_from_url(full_url)` -> `parsed.path.split('/')[-1]`. 
    # So `script src` becomes `.../critical.js`.
    # The import map currently has `.../critical.js?v=...`.
    # If I replace the prefix, I get `../assets/media/critical.js?v=...`.
    # Browser *will* try to load `critical.js` (ignoring query param usually, or treating it as distinct).
    # Since the file on disk is `critical.js`, this *should* work. 
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {file_path}")

def main():
    for root, dirs, files in os.walk(PROJECT_DIR):
        for file in files:
            if file.endswith('.html'):
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
