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
        var el = document.documentElement;
        var request = el.requestFullscreen || el.webkitRequestFullscreen || el.mozRequestFullScreen || el.msRequestFullscreen;
        if (request) {
          try {
            var result = request.call(el);
            if (result && result.catch) { result.catch(function() {}); }
          } catch (e) {}
        }
      }
      // Les navigateurs bloquent le plein ecran automatique sans un vrai
      // geste utilisateur. On tente au chargement (ca ne marchera que si
      // deja lance en PWA standalone), puis a CHAQUE clic/touch (pas
      // seulement le premier) pour permettre de repasser en plein ecran
      // apres en etre sorti. On ne le fait surtout PAS sur
      // 'visibilitychange' : ce n'est pas un geste utilisateur, et sortir
      // du plein ecran declenche cet evenement sur pas mal de navigateurs
      // mobiles -> le navigateur rejette l'appel et affiche une erreur de
      // permission a l'ecran.
      window.addEventListener('load', requestFullscreenSafe);
      document.addEventListener('click', requestFullscreenSafe);
      document.addEventListener('touchend', requestFullscreenSafe);
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

    # Le <meta charset> DOIT rester dans les 1024 premiers octets du
    # document (spec HTML5), sinon le navigateur peut se tromper
    # d'encodage pour parser le reste du <head> (manifest, icones...),
    # ce qui peut empecher la detection du manifest -> plus d'install
    # possible. Le template Unity met ce tag juste apres <head>, donc on
    # insere nos ajouts APRES lui (s'il existe) plutot qu'avant.
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
