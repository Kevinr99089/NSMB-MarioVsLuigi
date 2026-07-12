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
        // Deja en plein ecran : inutile de redemander, et un appel en trop
        // ici est justement ce qui declenche "Permissions check failed"
        // (activation utilisateur deja consommee par la 1ere demande).
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

      // Unity affiche une popup bloquante ("An error occurred running the
      // Unity content...") des qu'une exception JS remonte non interceptee
      // - meme si elle est totalement benigne. Notre propre tentative de
      // plein ecran ci-dessus est deja protegee (try/catch + .catch), mais
      // Unity a AUSSI sa propre logique de plein ecran interne (bouton du
      // player, raccourci clavier, option "Default Is Full Screen" du
      // build...) qui n'est pas protegee de notre cote. Quand le
      // navigateur refuse cette demande (geste utilisateur deja consomme,
      // plein ecran deja actif...), l'erreur "Permissions check failed"
      // remonte et Unity la traite comme fatale, alors que le jeu continue
      // de fonctionner normalement. Comme ce script s'execute juste apres
      // <head>, donc avant le runtime Unity (charge plus loin dans le
      // <body>), nos listeners 'error'/'unhandledrejection' sont
      // enregistres EN PREMIER : on peut donc intercepter precisement
      // cette erreur precise et empecher le gestionnaire d'Unity
      // (enregistre apres) de la recevoir, sans toucher aux vraies erreurs.
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
