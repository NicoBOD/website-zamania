/* ==========================================
   BARRE DE PROGRESSION DE LECTURE
   ==========================================
   Fine barre dorée en haut de l'écran indiquant la position dans
   l'article. L'élément est créé ici : aucune balise à ajouter aux pages.
   ========================================== */

(function () {
    'use strict';

    const article = document.querySelector('main article');
    if (!article) return;

    const bar = document.createElement('div');
    bar.className = 'reading-progress';
    bar.setAttribute('aria-hidden', 'true');
    document.body.appendChild(bar);

    let ticking = false;

    function update() {
        ticking = false;
        const rect = article.getBoundingClientRect();
        const total = rect.height - window.innerHeight;
        const progress = total > 0
            ? Math.min(1, Math.max(0, -rect.top / total))
            : 1;
        bar.style.width = (progress * 100) + '%';
    }

    window.addEventListener('scroll', function () {
        if (!ticking) {
            ticking = true;
            window.requestAnimationFrame(update);
        }
    }, { passive: true });

    window.addEventListener('resize', update, { passive: true });
    update();
})();
