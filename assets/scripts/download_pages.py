
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re

# Configuration
PROJECT_DIR = r"c:\Users\olato\OneDrive\Documents\Adechi website"
INDEX_FILE = os.path.join(PROJECT_DIR, 'index.html')
BASE_URL = "https://greedyunit.com"

# Setup directories
DIRS = ['products', 'collections', 'pages']
for d in DIRS:
    path = os.path.join(PROJECT_DIR, d)
    if not os.path.exists(path):
        os.makedirs(path)

def download_page(url, local_path):
    if os.path.exists(local_path):
        print(f"Skipping (exists): {local_path}")
        return True # Already exists

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        print(f"Downloading HTML: {url} -> {local_path}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # We need to save it. 
        # Note: The downloaded HTML will still have absolute links to /assets/ etc.
        # We might need to fix them to be relative to the new depth (e.g. "../assets/") or absolute "/assets/" if using server root.
        # check how the server is running. python -m http.server 8080 serves from root.
        # So "/assets/..." links work fine if they start with /. 
        # But our local links in index.html are currently "./assets/...". 
        # We should arguably switch everything to root-relative "/assets/..." to make it work from subdirectories too.
        
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def process_site():
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Find all internal links
    # logic: href starts with /products/, /collections/, /pages/
    # ignore /cart, /account, /search for now as they are likely dynamic
    
    links_found = 0
    
    for a in soup.find_all('a', href=True):
        href = a['href']
        
        # Strip query params for matching, but keep for downloading? 
        # Actually usually product pages like /products/wallet?variant=... point to same page.
        # We should download the base page.
        
        parsed = urlparse(href)
        path = parsed.path
        
        target_dir = None
        for d in DIRS:
            if path.startswith(f"/{d}/"):
                target_dir = d
                break
        
        if target_dir:
            # It's a key page
            slug = path.split('/')[-1]
            if not slug: continue # empty
            
            local_filename = f"{slug}.html"
            local_rel_path = f"{target_dir}/{local_filename}"
            local_abs_path = os.path.join(PROJECT_DIR, target_dir, local_filename)
            
            remote_url = urljoin(BASE_URL, path)
            
            # Download
            download_page(remote_url, local_abs_path)
            
            # Rewrite link in index.html
            # We want to keep query params if they exist in original href?
            # e.g. /products/hat?variant=123 -> products/hat.html?variant=123
            
            new_href = f"{local_rel_path}"
            if parsed.query:
                # new_href += f"?{parsed.query}" 
                # Actually, local file system doesn't handle query params well for opening files directly (file://), 
                # but http server works fine.
                pass 
            
            a['href'] = new_href
            links_found += 1

    # Save index.html
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(str(soup))
        
    print(f"Updated {INDEX_FILE} with {links_found} local links.")

if __name__ == "__main__":
    process_site()
