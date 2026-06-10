/* ==========================================
   CARROUSEL DES DERNIERS ARTICLES - ZAMANIA
   ==========================================

   Anime le bandeau défilant des derniers articles
   sur la page d'accueil (section #blog-preview) :

   1. Défilement automatique (pause au survol, au
      focus clavier, au toucher, hors écran, et
      désactivé si prefers-reduced-motion).
   2. Navigation par flèches et points de pagination.
   3. Resynchronisation : si la page d'accueil est en
      retard sur le blog (le pipeline n'a pas encore
      régénéré la section), les 5 dernières cartes
      sont rechargées depuis blog/index.html.

   Compatible RTL (version arabe) : les déplacements
   sont calculés via getBoundingClientRect, donc
   indépendants du sens d'écriture.
   ========================================== */

(function () {
    'use strict';

    var AUTOPLAY_DELAY = 4500;   // Délai entre deux avancées automatiques (ms)
    var MAX_ARTICLES = 5;        // Nombre d'articles affichés

    var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    var carousel = document.querySelector('.articles-carousel');
    if (!carousel) return;

    var track = carousel.querySelector('.carousel-track');
    var dotsContainer = carousel.querySelector('.carousel-dots');
    var prevBtn = carousel.querySelector('.carousel-prev');
    var nextBtn = carousel.querySelector('.carousel-next');
    if (!track) return;

    var cards = [];
    var dots = [];
    var currentIndex = 0;
    var autoplayTimer = null;
    var hovered = false;
    var focused = false;
    var visible = true;

    /* ---------- Navigation ---------- */

    // Centre la carte demandée dans la piste (fonctionne en LTR et RTL)
    function goTo(index, instant) {
        if (!cards.length) return;
        currentIndex = (index + cards.length) % cards.length;
        var trackRect = track.getBoundingClientRect();
        var cardRect = cards[currentIndex].getBoundingClientRect();
        var delta = (cardRect.left + cardRect.width / 2) - (trackRect.left + trackRect.width / 2);
        track.scrollBy({ left: delta, behavior: (reducedMotion || instant) ? 'auto' : 'smooth' });
    }

    // Détermine la carte la plus proche du centre de la piste
    function closestIndex() {
        var trackRect = track.getBoundingClientRect();
        var center = trackRect.left + trackRect.width / 2;
        var best = 0;
        var bestDist = Infinity;
        cards.forEach(function (card, i) {
            var r = card.getBoundingClientRect();
            var dist = Math.abs((r.left + r.width / 2) - center);
            if (dist < bestDist) {
                bestDist = dist;
                best = i;
            }
        });
        return best;
    }

    function updateDots() {
        dots.forEach(function (dot, i) {
            dot.classList.toggle('active', i === currentIndex);
            dot.setAttribute('aria-current', i === currentIndex ? 'true' : 'false');
        });
    }

    /* ---------- Défilement automatique ---------- */

    function stopAutoplay() {
        if (autoplayTimer) {
            clearInterval(autoplayTimer);
            autoplayTimer = null;
        }
    }

    function startAutoplay() {
        stopAutoplay();
        if (reducedMotion || hovered || focused || !visible || document.hidden) return;
        autoplayTimer = setInterval(function () {
            goTo(currentIndex + 1);
        }, AUTOPLAY_DELAY);
    }

    /* ---------- Construction / reconstruction ---------- */

    function setup() {
        cards = Array.prototype.slice.call(track.querySelectorAll('.carousel-card'));
        currentIndex = 0;

        if (dotsContainer) {
            dotsContainer.innerHTML = '';
            dots = cards.map(function (card, i) {
                var dot = document.createElement('button');
                dot.className = 'carousel-dot';
                dot.type = 'button';
                var title = card.querySelector('h3');
                dot.setAttribute('aria-label', title ? title.textContent.trim() : String(i + 1));
                dot.addEventListener('click', function () {
                    goTo(i);
                    startAutoplay();
                });
                dotsContainer.appendChild(dot);
                return dot;
            });
        }
        updateDots();
        startAutoplay();
    }

    /* ---------- Resynchronisation depuis le blog ---------- */

    // Reconstruit une carte du carrousel à partir d'une carte de blog/index.html.
    // Les chemins y sont relatifs au dossier blog/ : on les ramène à la racine
    // de la page d'accueil (un niveau au-dessus).
    function buildCard(blogCard) {
        var img = blogCard.querySelector('img');
        var date = blogCard.querySelector('.blog-card-date');
        var title = blogCard.querySelector('h3');
        var link = blogCard.querySelector('a');
        if (!img || !title || !link) return null;

        var card = document.createElement('article');
        card.className = 'blog-card carousel-card';

        var image = document.createElement('img');
        image.src = (img.getAttribute('src') || '').replace(/^\.\.\//, '');
        image.alt = img.getAttribute('alt') || title.textContent.trim();
        image.loading = 'lazy';

        var content = document.createElement('div');
        content.className = 'blog-card-content';

        var dateSpan = document.createElement('span');
        dateSpan.className = 'blog-card-date';
        dateSpan.textContent = date ? date.textContent.trim() : '';

        var heading = document.createElement('h3');
        heading.textContent = title.textContent.trim();

        var anchor = document.createElement('a');
        anchor.className = 'blog-card-link';
        anchor.href = 'blog/' + link.getAttribute('href');
        anchor.textContent = link.textContent.trim();

        content.appendChild(dateSpan);
        content.appendChild(heading);
        content.appendChild(anchor);
        card.appendChild(image);
        card.appendChild(content);
        return card;
    }

    function syncFromBlog() {
        var blogIndexUrl = carousel.getAttribute('data-blog-index') || 'blog/index.html';
        fetch(blogIndexUrl)
            .then(function (response) {
                if (!response.ok) throw new Error('HTTP ' + response.status);
                return response.text();
            })
            .then(function (html) {
                var doc = new DOMParser().parseFromString(html, 'text/html');
                var latest = Array.prototype.slice.call(doc.querySelectorAll('.blog-card')).slice(0, MAX_ARTICLES);
                if (!latest.length) return;

                var expected = latest.map(function (c) {
                    var a = c.querySelector('a');
                    return a ? (a.getAttribute('href') || '').split('/').pop() : '';
                });
                var current = cards.map(function (c) {
                    var a = c.querySelector('a');
                    return a ? (a.getAttribute('href') || '').split('/').pop() : '';
                });
                if (expected.join('|') === current.join('|')) return;

                var fresh = latest.map(buildCard).filter(Boolean);
                if (!fresh.length) return;

                cards.forEach(function (c) { c.remove(); });
                fresh.forEach(function (c) { track.appendChild(c); });
                setup();
            })
            .catch(function () {
                /* Hors-ligne ou blog inaccessible : on garde les cartes statiques */
            });
    }

    /* ---------- Écouteurs ---------- */

    if (prevBtn) prevBtn.addEventListener('click', function () { goTo(currentIndex - 1); startAutoplay(); });
    if (nextBtn) nextBtn.addEventListener('click', function () { goTo(currentIndex + 1); startAutoplay(); });

    carousel.addEventListener('pointerenter', function () { hovered = true; stopAutoplay(); });
    carousel.addEventListener('pointerleave', function () { hovered = false; startAutoplay(); });
    carousel.addEventListener('focusin', function () { focused = true; stopAutoplay(); });
    carousel.addEventListener('focusout', function () { focused = false; startAutoplay(); });
    track.addEventListener('touchstart', stopAutoplay, { passive: true });
    track.addEventListener('touchend', startAutoplay, { passive: true });

    document.addEventListener('visibilitychange', startAutoplay);

    // Pause quand le carrousel sort de l'écran
    if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (entries) {
            visible = entries[0].isIntersecting;
            startAutoplay();
        }, { threshold: 0.25 }).observe(carousel);
    }

    // Suivi du point actif pendant un défilement manuel
    var scrollRaf = null;
    track.addEventListener('scroll', function () {
        if (scrollRaf) return;
        scrollRaf = requestAnimationFrame(function () {
            scrollRaf = null;
            currentIndex = closestIndex();
            updateDots();
        });
    }, { passive: true });

    setup();
    syncFromBlog();
})();
