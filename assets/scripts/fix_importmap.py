
import os
import re

PROJECT_DIR = r"c:\Users\olato\OneDrive\Documents\Adechi website"

def fix_import_map(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Match the import map block
    # We want to find cases where it says assets/media/something.js and change it to assets/js/something.js
    # Only inside the imports block
    
    new_content = re.sub(r'(assets)/media/([^"\']+\.js)', r'\1/js/\2', content)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Force-fixed importmap in {file_path}")

def main():
    for root, dirs, files in os.walk(PROJECT_DIR):
        for file in files:
            if file.endswith('.html'):
                fix_import_map(os.path.join(root, file))

if __name__ == "__main__":
    main()
