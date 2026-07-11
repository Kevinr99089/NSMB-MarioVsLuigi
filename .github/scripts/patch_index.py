import re
import sys

HEAD_ADDITIONS = """
    <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <link rel="manifest" href="manifest.json">
    <link rel="icon" href="icon-192.png">
    <link rel="apple-touch-icon" href="icon-192.png">
    <meta name="theme-color" content="#1e1e28">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <style>html, body { overscroll-behavior: none; touch-action: manipulation; }</style>
    <script>
      if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => { navigator.serviceWorker.register('sw.js'); });
      }
    </script>
"""

def main():
    if len(sys.argv) != 2:
        print("Usage: patch_index.py <path-to-index.html>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if "manifest.json" in content:
        print("index.html deja patche, rien a faire")
        return

    new_content, count = re.subn(r"(<head[^>]*>)", r"\1" + HEAD_ADDITIONS, content, count=1)

    if count == 0:
        print("Balise <head> introuvable, patch non applique")
        sys.exit(1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("index.html patche avec succes")

if __name__ == "__main__":
    main()
