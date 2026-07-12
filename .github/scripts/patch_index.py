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
      function requestFullscreenSafe() {
        if (document.fullscreenElement) return;
        var el = document.documentElement;
        var request = el.requestFullscreen || el.webkitRequestFullscreen || el.mozRequestFullScreen || el.msRequestFullscreen;
        if (request) {
          try {
            var result = request.call(el);
            if (result && result.catch) { result.catch(function() {}); }
          } catch (e) {}
        }
      }
      window.addEventListener('load', requestFullscreenSafe);
      document.addEventListener('click', requestFullscreenSafe);
      document.addEventListener('touchend', requestFullscreenSafe);
      if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => { navigator.serviceWorker.register('sw.js'); });
      }
      function isBenignFullscreenPermissionError(err) {
        return err instanceof TypeError && err.message === 'Permissions check failed';
      }
      window.addEventListener('error', function(event) {
        if (isBenignFullscreenPermissionError(event.error)) {
          event.stopImmediatePropagation();
          event.preventDefault();
        }
      });
      window.addEventListener('unhandledrejection', function(event) {
        if (isBenignFullscreenPermissionError(event.reason)) {
          event.stopImmediatePropagation();
          event.preventDefault();
        }
      });
      function hookUnityQuit(unityInstance) {
        var module = unityInstance && unityInstance.Module;
        if (!module) return;
        module.onQuit = function() {
          var isStandalone = window.matchMedia('(display-mode: standalone)').matches ||
            window.matchMedia('(display-mode: fullscreen)').matches ||
            window.navigator.standalone === true;
          function showQuitMessage() {
            document.body.innerHTML =
              '<div style="position:fixed;inset:0;display:flex;align-items:center;' +
              'justify-content:center;background:#1e1e28;color:#fff;' +
              'font-family:sans-serif;font-size:1.1rem;text-align:center;' +
              'padding:2rem;">Jeu quitte. Vous pouvez fermer cette fenetre.</div>';
          }
          if (document.fullscreenElement) {
            (document.exitFullscreen || function() {}).call(document).catch(function() {});
          }
          if (isStandalone) {
            showQuitMessage();
            return;
          }
          try { window.close(); } catch (e) {}
          setTimeout(showQuitMessage, 300);
        };
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
    then_re = re.compile(r"(\.then\(\s*\(?\s*(\w+)\s*\)?\s*=>\s*\{)")
    content, then_count = then_re.subn(
        lambda m: m.group(1) + "\n        hookUnityQuit(" + m.group(2) + ");",
        content,
        count=1,
    )
    if then_count == 0:
        print("Avertissement : callback createUnityInstance(...).then(...) introuvable, gestion du Quit non branchee")
    head_re = re.compile(r"<head[^>]*>\s*(?:<meta[^>]+charset[^>]*>\s*)?", re.IGNORECASE)
    new_content, count = head_re.subn(lambda m: m.group(0) + HEAD_ADDITIONS, content, count=1)
    if count == 0:
        print("Balise <head> introuvable, patch non applique")
        sys.exit(1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("index.html patche avec succes")
if __name__ == "__main__":
    main()
