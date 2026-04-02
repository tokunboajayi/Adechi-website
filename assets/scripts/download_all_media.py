
import os
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote

# Configuration
PROJECT_DIR = r"c:\Users\olato\OneDrive\Documents\Adechi website"
# HTML_FILE = os.path.join(PROJECT_DIR, 'index.html') # Process all htmls now
MEDIA_DIR_REL = 'assets/media'
MEDIA_DIR = os.path.join(PROJECT_DIR, MEDIA_DIR_REL)

DOMAINS_TO_DOWNLOAD = ['cdn.shopify.com', 'greedyunit.com', 'greedyunit.myshopify.com']

# Ensure media directory exists
if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)

def get_filename_from_url(url):
    parsed = urlparse(url)
    path = unquote(parsed.path)
    filename = os.path.basename(path)
    
    # Remove query parameters from filename if present in path (unlikely for shopify usually)
    # But often shopify URLs are like /.../file.jpg?v=...
    # We want file.jpg
    
    # Sanitize filename
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # If filename is empty or too short, use a hash
    if not filename or len(filename) < 3 or filename == 'aaa': # dummy
        filename = f"asset_{abs(hash(url))}.ext" 
        
    return filename

def download_file(url, local_path):
    if os.path.exists(local_path):
        # file exists, skip? or overwrite? let's skip for speed
        return True

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        print(f"Downloading: {url} -> {local_path}")
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def process_html_file(file_path):
    print(f"Processing {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    # Calculate depth to fix relative paths
    # index.html (root) -> assets/media/file.jpg
    # products/hat.html (depth 1) -> ../assets/media/file.jpg
    
    rel_path_from_root = os.path.relpath(file_path, PROJECT_DIR)
    depth = len(rel_path_from_root.split(os.sep)) - 1
    
    media_prefix = "./" + MEDIA_DIR_REL + "/"
    if depth > 0:
        media_prefix = "../" * depth + MEDIA_DIR_REL + "/"
        
    # Also we need to fix CSS/JS links if they are relative!
    # But let's focus on media download first.

    tags_to_scan = [
        ('img', ['src', 'srcset', 'data-src', 'data-srcset']),
        ('video', ['src', 'poster']),
        ('source', ['src', 'srcset']),
        ('link', ['href']), 
        ('script', ['src']), 
        ('a', ['href']),
    ]

    count = 0

    for tag_name, attributes in tags_to_scan:
        for tag in soup.find_all(tag_name):
            for attr in attributes:
                if not tag.has_attr(attr):
                    continue
                
                original_value = tag[attr]
                if not original_value: continue

                # Helper to process a single URL
                def process_url(url_val):
                    url_val = url_val.strip()
                    if not url_val: return url_val
                    
                    is_target = False
                    if 'cdn.shopify.com' in url_val: is_target = True
                    if 'greedyunit.com/cdn' in url_val: is_target = True
                    if url_val.startswith('/cdn/'): is_target = True
                    
                    full_url = url_val
                    if url_val.startswith('//'):
                        full_url = 'https:' + url_val
                    elif url_val.startswith('/cdn/'): 
                         full_url = 'https://greedyunit.com' + url_val
                    elif url_val.startswith('/') and not url_val.startswith('/products') and not url_val.startswith('/collections') and not url_val.startswith('/pages'):
                        # potentially other assets like /checkouts/ ... but careful not to download pages as assets
                        pass

                    if not is_target and 'http' in full_url and 'shopify' in full_url:
                        is_target = True
                    
                    if not is_target and 'greedyunit.com' in full_url and ('/cdn/' in full_url or '.css' in full_url or '.js' in full_url):
                        is_target = True
                    
                    if not is_target:
                        return url_val

                    filename = get_filename_from_url(full_url)
                    local_abs_path = os.path.join(MEDIA_DIR, filename)
                    
                    if download_file(full_url, local_abs_path):
                        return f"{media_prefix}{filename}"
                    else:
                        return url_val

                # Handle srcset...
                if 'srcset' in attr:
                    parts = original_value.split(',')
                    new_parts = []
                    for part in parts:
                        part = part.strip()
                        if not part: continue
                        subparts = part.strip().split(' ')
                        url = subparts[0]
                        descriptor = ' '.join(subparts[1:]) if len(subparts) > 1 else ''
                        new_url = process_url(url)
                        if new_url != url:
                             new_parts.append(f"{new_url} {descriptor}".strip())
                        else:
                             new_parts.append(part)
                    tag[attr] = ', '.join(new_parts)
                    if tag[attr] != original_value: count += 1

                else:
                    new_val = process_url(original_value)
                    if new_val != original_value:
                        tag[attr] = new_val
                        count += 1

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(f"Updated {count} attributes in {file_path}.")

def process_all():
    for root, dirs, files in os.walk(PROJECT_DIR):
        for file in files:
            if file.endswith('.html'):
                process_html_file(os.path.join(root, file))

if __name__ == "__main__":
    process_all()
