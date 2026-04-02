<div align="center">
  <img src="assets/media/og_image.webp" alt="GREEDY(UNIT) Logo" width="150">
  
  # Adechi Website – GREEDY(UNIT)

  ![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
  ![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
  ![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)

  **A headless, static reconstruction of the GREEDY(UNIT) Shopify frontend.**

</div>

---

## 📖 Table of Contents
1. [Project Overview](#-project-overview)
2. [Interactive Directory Structure](#-interactive-directory-structure)
3. [Quick Start (Local Development)](#-quick-start)
4. [Current State & Known Limitations](#-current-state--known-limitations)
5. [Roadmap & Next Steps](#-roadmap--next-steps)

---

## 🚀 Project Overview

This repository contains the static frontend extraction of the **GREEDY(UNIT)** e-commerce website. The purpose of this project is to maintain, optimize, and safely test UI/UX updates before pushing them to the production Shopify theme architecture. 

It contains standard web assets (HTML, CSS, JS) decoupled from Shopify Liquid to allow for rapid, offline layout testing.

---

## 📁 Interactive Directory Structure

Click on any folder below to expand and see what it contains!

<details>
  <summary><b>📂 assets/</b> (Static Resources)</summary>

  - **`css/`**: Core stylesheets, including `theme.css` and typography logic.
  - **`fonts/`**: Includes our `.woff2` font variants (like `inter_n4`).
  - **`media/` & `images/`**: Product imagery, icons (like `Greedy_Cart_Icon.png`), and promotional videos.
  - **`js/`**: Client-side scripts controlling animations, headers, and Shopify tracking.
</details>

<details>
  <summary><b>📂 collections/</b> (Product Grids)</summary>

  - Contains `.html` files for the various product groupings (e.g., `home-featured-copy.html`, `tdr-collab.html`).
</details>

<details>
  <summary><b>📂 products/</b> (Product Description Pages - PDP)</summary>

  - Deeply linked individual product pages natively exported from Shopify (e.g., `pesos-wallet.html`, `thrashed-denim.html`).
</details>

<details>
  <summary><b>📄 Root Files</b></summary>
  
  - **`index.html`**: The main landing page / entry point for the offline storefront.
  - **`README.md`**: You are here!
</details>

---

## 💻 Quick Start

To preview this website locally and properly resolve the localized assets (without dealing with CORS or paths breaking), you need to run a local development server.

### Prerequisites
Make sure you have **Python 3** installed on your machine.

### Step-by-Step
1. Open your terminal and navigate to the root directory of this project:
   ```bash
   cd "path/to/Adechi website"
   ```
2. Start the local server by running:
   ```bash
   python -m http.server 8080 --bind 127.0.0.1
   ```
3. Open your browser and visit:
   [http://127.0.0.1:8080](http://127.0.0.1:8080)

> **Pro Tip:** Alternatively, if you have Node.js installed, you can use `npx http-server -p 8080` for a faster testing experience.

---

## ⚠️ Current State & Known Limitations

> [!WARNING]
> Because this is a static representation of a Shopify storefront, several dynamic features are currently inert.

1. **Add to Cart (POST Error):** Clicking "Place In Cart" on product pages currently results in a `501 Unsupported Method ('POST')` error on the local server. The JavaScript attempts to hit Shopify's `/cart/update.js`, which our local Python server cannot handle natively. 
2. **Missing Contact Pages / 404s:** Forms and contact submissions will not operate locally. Link integrations intended for dynamic Shopify routing (`/pages/contact`) will lead to 404s locally if the static `.html` doesn't exist.

---

## 🗺️ Roadmap & Next Steps

* [x] Fix lagging missing asset endpoints (Localizing `Greedy_Menu`, `Greedy_Cart_Icon`, and Inter Typography fonts).
* [x] Remove legacy/outdated collections directly from the homepage.
* [ ] **Target:** Implement a Mock Server (Node.js/Express) to intercept Cart `POST` requests and fake the UI animations locally.
* [ ] **Target:** Move the application back into a full **Shopify Theme App CLI** environment for fully integrated production tests.

---
<div align="center">
  <i>Maintained by the GREEDY(UNIT) Development Team</i>
</div>
