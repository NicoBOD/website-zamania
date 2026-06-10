/* ==========================================
   PARTAGE D'ARTICLE
   ==========================================
   Bouton « copier le lien » du bloc de partage : partage natif du
   téléphone quand il existe (navigator.share), sinon copie dans le
   presse-papiers avec un retour visuel localisé (attribut data-copied).
   ========================================== */

(function () {
    'use strict';

    const button = document.querySelector('.share-copy');
    if (!button) return;

    function pageUrl() {
        const canonical = document.querySelector('link[rel="canonical"]');
        return canonical ? canonical.href : window.location.href;
    }

    function showFeedback() {
        let note = button.parentElement.querySelector('.share-copy-feedback');
        if (!note) {
            note = document.createElement('span');
            note.className = 'share-copy-feedback';
            note.setAttribute('role', 'status');   /* annoncé aux lecteurs d'écran */
            button.parentElement.appendChild(note);
        }
        note.textContent = button.dataset.copied || '';
        clearTimeout(note._timer);
        note._timer = setTimeout(function () { note.textContent = ''; }, 2500);
    }

    function legacyCopy(text) {
        const area = document.createElement('textarea');
        area.value = text;
        area.style.position = 'fixed';
        area.style.opacity = '0';
        document.body.appendChild(area);
        area.select();
        document.execCommand('copy');
        area.remove();
    }

    button.addEventListener('click', async function () {
        const url = pageUrl();

        /* Sur mobile, la feuille de partage native est plus utile qu'une copie */
        if (navigator.share) {
            try {
                await navigator.share({ title: document.title, url: url });
                return;
            } catch (err) {
                if (err && err.name === 'AbortError') return;  /* fermé par l'utilisateur */
            }
        }

        try {
            await navigator.clipboard.writeText(url);
        } catch (err) {
            legacyCopy(url);
        }
        showFeedback();
    });
})();
