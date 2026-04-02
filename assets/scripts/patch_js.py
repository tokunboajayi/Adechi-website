
import os

PROJECT_DIR = r"c:\Users\olato\OneDrive\Documents\Adechi website"
JS_DIR = os.path.join(PROJECT_DIR, "assets", "js")

def patch_product_card_js():
    file_path = os.path.join(JS_DIR, "product-card.js")
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Fix #navigateToURL to NOT open new windows or redirect if it can be helped,
    # or ensure it uses the .href which we already rewrote.
    # The code:
    # #navigateToURL=(event,url)=>{if(event instanceof MouseEvent&&(event.metaKey||event.ctrlKey||event.shiftKey||event.button===1)){event.preventDefault(),window.open(url.href,"_blank");return}else window.location.href=url.href};
    # This actually looks OK, it uses url.href.
    
    # 2. Fix navigateToProduct
    # const linkURL=new URL(link.href),productCardAnchor=link.getAttribute("id");
    # if(!productCardAnchor)return;
    # const url=new URL(window.location.href),parent=this.closest("li");
    # url.hash=productCardAnchor, ...
    # window.location.href=url.toString()
    
    # ISSUE: This logic seems to trigger when there is a productCardAnchor (ID on the link?).
    # If the link has an ID, it tries to stay on the same page and set a hash?
    # Let's see the HTML in index.html (Step 5318):
    # <a ... href="products/thrashed-denim.html" ref="cardGalleryLink">
    # It does NOT have an 'id' attribute. It has 'ref'.
    # So `productCardAnchor` should be null.
    # So `navigateToProduct` should hit `event.target.closest("a")||this.#navigateToURL(event,linkURL)`.
    
    # Wait, `event.target.closest("a")`?
    # If I click the image, `event.target` is `img`. `closest("a")` is the link.
    # So it returns (does nothing), allowing default browser navigation?
    # `event.target.closest("a")||this.#navigateToURL(event,linkURL)`
    # This means: If clicked inside an 'a', do nothing (return).
    # Else, call #navigateToURL.
    
    # If I click the image, it IS inside an 'a'. So it returns.
    # The browser then follows the 'a'.
    # The 'a' href is `products/thrashed-denim.html`.
    # So it SHOULD work.
    
    # BUT, `variant-picker.js` also has navigation logic.
    # `const currentUrl=this.dataset.productUrl?.split("?")[0],newUrl=selectedOption.dataset.connectedProductUrl`
    # `loadsNewProduct=...`
    # `url.href!==window.location.href&&requestYieldCallback(()=>{history.replaceState({},"",url.toString())})`
    # Only `replaceState`, so it updates URL bar but doesn't reload.
    
    # However, `product-card.js` also has `#updateProductUrl`.
    # `productCardLink.href=productUrl`
    # If `productUrl` comes from `event.detail.data.html` (fetched from server?),
    # and the server returns HTML with CLEAN URLs (because it's just fetching text?),
    # THEN the href becomes clean (broken).
    
    # But we are offline. `fetch` calls will fail or return local HTML.
    # If they fetch `products/thrashed-denim.html`, they get the file content.
    # Does that file content have clean URLs or rewritten URLs?
    # My `download_pages.py` rewrote links in `products/*.html`.
    # But `product-card.js` logic: `const anchorElement=event.detail.data.html?.querySelector("product-card a")`
    # It extracts href from the fetched HTML.
    
    # If I am on `index.html`, and I click to go to product page... `product-card.js` shouldn't be fetching anything yet?
    # Unless I hover? `#handleQuickAdd` adds `pointerenter` listener to `#fetchProductPageHandler`.
    # `#fetchProductPageHandler` calls `this.refs.quickAdd?.fetchProductPage(this.productPageUrl)`.
    # `quickAdd` is `QuickAdd` component (in `quick-add.js`?).
    
    # `QuickAdd` fetches the product page to pre-load data?
    # If it fetches `products/thrashed-denim.html`, it gets the HTML.
    # Then `product-card.js` might parse it and UPDATE the link `href`?
    # `#updateProductUrl` uses `anchorElement.href`.
    
    # If the fetched HTML has `<a href="...">` ...
    # In `products/thrashed-denim.html`, what is the "product-card a"?
    # The product page itself might not have a "product-card" for itself?
    # Or maybe it does (Related Products?).
    
    # HYPOTHESIS: The `fetch` might be failing or returning something unexpected,
    # OR the `quick-add` logic is interfering.
    
    # REMEDY: Disable the `fetchProductPageHandler` or `updateProductUrl` logic in `product-card.js`.
    # We don't need "Quick Add" pre-fetching offline.
    
    print("Patching product-card.js...")
    # Disable pre-fetching on hover
    new_content = content.replace('this.addEventListener("pointerenter",this.#fetchProductPageHandler)', '//this.addEventListener("pointerenter",this.#fetchProductPageHandler)')
    new_content = new_content.replace('this.addEventListener("focusin",this.#fetchProductPageHandler)', '//this.addEventListener("focusin",this.#fetchProductPageHandler)')
    
    # Disable #navigateToURL just in case, or force it to use .html?
    # Actually, preventing the pre-fetch is safer.
    
    # Also disable `window.location.href=url.href` in `#navigateToURL`?
    # If it's a direct assignment, we want to ensure it ends in .html?
    # No, if the URL object is correct, it's fine.
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Updated product-card.js")
    else:
        print("product-card.js already patched or pattern not found")

def patch_variant_picker_js():
    file_path = os.path.join(JS_DIR, "variant-picker.js")
    if not os.path.exists(file_path):
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Disable history manipulation that might accidentally remove .html
    # `history.replaceState`
    
    new_content = content.replace('history.replaceState', '//history.replaceState')
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Updated variant-picker.js")

def main():
    patch_product_card_js()
    patch_variant_picker_js()

if __name__ == "__main__":
    main()
