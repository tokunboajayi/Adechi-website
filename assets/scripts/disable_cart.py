
import os

PROJECT_DIR = r"c:\Users\olato\OneDrive\Documents\Adechi website"

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace action="/cart/add" with action="javascript:void(0)" and onsubmit="..."
    new_content = content.replace('action="/cart/add"', 'action="javascript:void(0)" onsubmit="alert(\'Cart functionality is not available offline.\'); return false;"')
    
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
