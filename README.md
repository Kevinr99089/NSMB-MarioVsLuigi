# New Super Mario Bros. — Mario Vs Luigi (PWA & WebGL Edition)

An unofficial, automated deployment fork of the [NSMB-MarioVsLuigi](https://github.com/ipodtouch0218/NSMB-MarioVsLuigi) project developed by **ipodtouch0218**.

This repository provides a fully automated pipeline to fetch, extract, and adapt the original WebGL release into a compliant Progressive Web App (PWA), optimized for instant access and seamless installation on Android, as well as desktop and mobile browsers.

---

## ⚙️ Automated Workflow & Architecture

This project functions as an automated deployment layer on top of the upstream source. The integrated automation pipeline executes the following operations:
* **Upstream Monitoring:** Automatically tracks and fetches the latest `MarioVsLuigi-WebGL-vx.x.x.zip` release from the main repository.
* **Asset Extraction:** Extracts the WebGL bundle directly into the `/docs/` directory, making it ready for deployment via GitHub Pages.
* **PWA Enhancement:** Dynamically modifies the generated `index.html` file to inject a Web App Manifest, Service Worker registrations, and mobile viewport optimizations required for native PWA capabilities.

---

## 📱 Features & Mobile Optimization

By wrapping the WebGL build into a Progressive Web App structure, this deployment delivers several key advantages:
* **Native Standalone Experience:** On Android and compatible platforms, the game can be installed directly onto the home screen, launching in full-screen mode without browser navigation bars.
* **Zero-Overhead Playback:** Eliminates the need for traditional manual installation or third-party sideloading; players can access the game instantly via a URL.
* **Continuous Updates:** Thanks to the automated workflow, upstream updates and performance enhancements from the original project can be integrated seamlessly.

---

## 🎮 Access & Installation Instructions

### Web Access
The game can be played instantly by visiting this [GitHub Pages](https://Kevinr99089.github.io/NSMB-MarioVsLuigi/)

### Installing as a PWA (Android / Google Chrome)
1. Navigate to the deployment URL using Google Chrome on an Android device.
2. Tap the menu icon (three vertical dots) in the top-right corner.
3. Select **"Add to Home screen"** or **"Install app"**.
4. Confirm the installation. The game will now be available as a standalone app icon in your app drawer.

---

## ❤️ Upstream Credits & Support

This repository is a passive distribution and optimization fork. Full credit for the core game development, asset reverse-engineering, netcode, and design goes entirely to **ipodtouch0218** and the upstream project's contributors. 

Please visit, star, and support the original project:
👉 **[ipodtouch0218/NSMB-MarioVsLuigi](https://github.com/ipodtouch0218/NSMB-MarioVsLuigi)**

*Note: For gameplay bugs, feature requests regarding the core mechanics, or to contribute to the engine itself, please refer directly to the upstream repository.*
