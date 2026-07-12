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

      // Quand on clique sur "Quitter" DANS le jeu, Application.Quit() (cote
      // C#) appelle en interne Module.QuitCleanup() : ca coupe le rendu,
      // l'audio, les inputs... puis ca verifie si "Module.onQuit" est une
      // fonction, et si oui l'appelle. Par defaut ce callback n'existe pas,
      // donc apres le nettoyage il ne se passe RIEN de plus : la derniere
      // image reste figee a l'ecran, plus de son, la page ne se ferme
      // jamais. Ce n'est pas un bug du jeu : Unity attend que ce soit LA
      // PAGE (nous) qui decide quoi faire au moment ou le jeu quitte. On
      // definit donc onQuit nous-memes, des que le player est pret.
      //
      // Pour recuperer l'instance Unity sans dependre du script inline
      // genere par Unity (createUnityInstance(canvas, config).then(...)),
      // on intercepte la fonction globale "createUnityInstance" elle-meme :
      // Build/*.loader.js la declare (function createUnityInstance(...))
      // APRES ce script <head>, donc en definissant la propriete window
      // avec configurable:false et un accesseur get/set AVANT que ce
      // fichier ne se charge, la declaration globale du loader passe par
      // notre "set" (c'est le comportement standard du JS pour une
      // declaration de fonction globale qui rencontre une propriete non
      // configurable) au lieu d'ecraser notre accesseur. On peut alors
      // envelopper la vraie fonction sans toucher au script inline d'Unity,
      // ce qui reste valide meme si Unity regenere ce template plus tard.
      (function() {
        var realCreateUnityInstance = null;
        Object.defineProperty(window, 'createUnityInstance', {
          configurable: false,
          enumerable: true,
          get: function() {
            return function(canvas, config, onProgress) {
              return realCreateUnityInstance(canvas, config, onProgress).then(function(unityInstance) {
                hookUnityQuit(unityInstance);
                return unityInstance;
              });
            };
          },
          set: function(fn) { realCreateUnityInstance = fn; }
        });
      })();

      function hookUnityQuit(unityInstance) {
        var module = unityInstance && unityInstance.Module;
        if (!module) return;
        module.onQuit = function() {
          // On sort du plein ecran pour que la suite (fermeture ou message)
          // soit visible, meme si window.close() est refuse.
          if (document.fullscreenElement) {
            (document.exitFullscreen || function() {}).call(document).catch(function() {});
          }
          try { window.close(); } catch (e) {}
          // Si la fenetre est toujours la apres un court delai, c'est que
          // le navigateur a refuse window.close() (restriction standard :
          // un script ne peut fermer que les fenetres/onglets qu'il a
          // lui-meme ouverts). Dans ce cas, on affiche un message clair
          // plutot que de laisser la derniere image du jeu figee sans
          // explication.
          setTimeout(function() {
            document.body.innerHTML =
              '<div style="position:fixed;inset:0;display:flex;align-items:center;' +
              'justify-content:center;background:#1e1e28;color:#fff;' +
              'font-family:sans-serif;font-size:1.1rem;text-align:center;' +
              'padding:2rem;">Jeu quitte. Vous pouvez fermer cette fenetre.</div>';
          }, 300);
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
