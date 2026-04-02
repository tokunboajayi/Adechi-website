
import os
import re
from bs4 import BeautifulSoup

PROJECT_DIR = r"c:\Users\olato\OneDrive\Documents\Adechi website"
ASSETS_REL = "assets"

# Categories mapping to folders
EXT_MAP = {
    '.js': 'js',
    '.css': 'css',
    '.woff2': 'fonts', '.woff': 'fonts', '.ttf': 'fonts', '.otf': 'fonts',
    '.jpg': 'media', '.jpeg': 'media', '.png': 'media', '.gif': 'media',
    '.svg': 'media', '.mp4': 'media', '.webp': 'media', '.ico': 'media'
}

def get_rel_assets_path(file_path):
    rel_from_root = os.path.relpath(file_path, PROJECT_DIR)
    depth = len(rel_from_root.split(os.sep)) - 1
    if depth == 0:
        return ASSETS_REL
    else:
        return "../" * depth + ASSETS_REL

def fix_url(val, rel_assets):
    # If already a local relative path, just ensure it's categorized
    # But mostly we want to catch remote or absolute-style paths
    if 'shopify' in val or 'greedyunit' in val or '/cdn/' in val or 'assets/' in val:
        # Find matching extension
        found_ext = None
        for ext in EXT_MAP:
            if ext in val.lower():
                found_ext = ext
                break
        
        if found_ext:
            folder = EXT_MAP[found_ext]
            # Extract filename
            filename = val.split('/')[-1].split('?')[0]
            return f"{rel_assets}/{folder}/{filename}"
    return val

def repair_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    rel_assets = get_rel_assets_path(file_path)
    
    modified = False

    # 1. Fix Asset Tags (img, video, link, script, etc.)
    tags = {
        'img': ['src', 'srcset', 'data-src', 'data-srcset'],
        'video': ['src', 'poster'],
        'source': ['src', 'srcset'],
        'link': ['href'],
        'script': ['src']
    }

    for tag_name, attrs in tags.items():
        for el in soup.find_all(tag_name):
            for attr in attrs:
                if el.has_attr(attr):
                    val = el[attr]
                    if ',' in val: # srcset
                        parts = val.split(',')
                        new_parts = []
                        for part in parts:
                            sub_parts = part.strip().split(' ')
                            url = sub_parts[0]
                            new_url = fix_url(url, rel_assets)
                            if len(sub_parts) > 1:
                                new_parts.append(f"{new_url} {sub_parts[1]}")
                            else:
                                new_parts.append(new_url)
                        new_val = ", ".join(new_parts)
                        if el[attr] != new_val:
                            el[attr] = new_val
                            modified = True
                    else:
                        new_val = fix_url(val, rel_assets)
                        if el[attr] != new_val:
                            el[attr] = new_val
                            modified = True

    # 2. Fix Style Tags (CSS URLs)
    for style in soup.find_all('style'):
        if style.string:
            # Match url("...") or url(...)
            def replace_css_url(match):
                url = match.group(2) or match.group(3)
                if url:
                    return f'url("{fix_url(url, rel_assets)}")'
                return match.group(0)
            
            new_css = re.sub(r'url\((["\'])([^"\']+)\1\)|url\(([^)]+)\)', replace_css_url, style.string)
            if new_css != style.string:
                style.string = new_css
                modified = True

    # 3. Fix Internal Links (a href)
    for a in soup.find_all('a', href=True):
        href = a['href']
        # Handle links like /products/something -> products/something.html
        if href.startswith('/products/') or href.startswith('/collections/') or href.startswith('/pages/'):
            rel_to_root = ""
            rel_from_root = os.path.relpath(file_path, PROJECT_DIR)
            depth = len(rel_from_root.split(os.sep)) - 1
            if depth > 0: rel_to_root = "../" * depth
            
            clean_path = href.lstrip('/')
            if not clean_path.endswith('.html'):
                clean_path = clean_path.split('?')[0]
                new_href = rel_to_root + clean_path + ".html"
                if a['href'] != new_href:
                    a['href'] = new_href
                    modified = True
        elif ('products/' in href or 'collections/' in href) and not href.endswith('.html'):
             # Ensure extension
             if 'javascript:' not in href and '#' not in href and ':' not in href:
                new_href = href.split('?')[0] + ".html"
                if a['href'] != new_href:
                    a['href'] = new_href
                    modified = True

    # 4. Disable Cart and Search Forms
    for form in soup.find_all('form'):
        action = form.get('action', '')
        if '/cart/add' in action or '/search' in action:
            form['action'] = 'javascript:void(0)'
            form['onsubmit'] = "alert('This feature is not available offline.'); return false;"
            modified = True

    # 5. Patch Import Map
    import_map = soup.find('script', type='application/importmap')
    if import_map:
        try:
            import json
            # We'll use a more direct approach since soup.string might be tricky with prettify
            data = json.loads(import_map.string)
            if 'imports' in data:
                new_imports = {}
                for key, val in data['imports'].items():
                    # Handle versioned URLs: path/to/file.js?v=123
                    filename_with_query = val.split('/')[-1]
                    filename_only = filename_with_query.split('?')[0]
                    
                    if filename_only.endswith('.js'):
                        new_imports[key] = f"{rel_assets}/js/{filename_with_query}"
                    elif any(filename_only.endswith(ext) for ext in ['.woff', '.woff2', '.ttf', '.otf']):
                         new_imports[key] = f"{rel_assets}/fonts/{filename_with_query}"
                    elif any(filename_only.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp', '.svg']):
                         new_imports[key] = f"{rel_assets}/media/{filename_with_query}"
                    else:
                        new_imports[key] = fix_url(val, rel_assets)
                data['imports'] = new_imports
                # Replace the entire script content
                import_map.string = json.dumps(data, indent=2)
                modified = True
        except Exception as e:
            print(f"Error patching import map in {file_path}: {e}")

    # 6. Patch Inline Scripts (basePath etc)
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string:
            if "const basePath =" in script.string:
                new_string = re.sub(r"const basePath = '[^']+';", f"const basePath = '.';", script.string)
                if new_string != script.string:
                    script.string = new_string
                    modified = True

    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f"Repaired {file_path}")

def main():
    for root, dirs, files in os.walk(PROJECT_DIR):
        for file in files:
            if file.endswith('.html'):
                repair_content(os.path.join(root, file))

if __name__ == "__main__":
    main()
