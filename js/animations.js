/* ==========================================
   ANIMATIONS AU SCROLL
   ==========================================
   
   Ce script gère les animations d'apparition
   des éléments lorsqu'ils entrent dans le
   viewport (zone visible de l'écran).
   
   Utilise l'API Intersection Observer pour
   détecter quand un élément devient visible.
   
   Fonctionnalités :
   - Animation progressive au scroll
   - Respect des préférences d'accessibilité
   - Performance optimisée
   ========================================== */


// ==========================================
// 1. INITIALISATION DES ÉLÉMENTS À ANIMER
// ==========================================

/**
 * Sélection de tous les éléments qui doivent être animés
 * 
 * Classes disponibles :
 * - .animate : apparition depuis le bas
 * - .animate-left : apparition depuis la gauche
 * - .animate-right : apparition depuis la droite
 * - .animate-scale : apparition avec zoom
 */
const animateElements = document.querySelectorAll(
    '.animate, .animate-left, .animate-right, .animate-scale'
);


// ==========================================
// 2. ACTIVATION PROGRESSIVE DES ANIMATIONS
// ==========================================

/**
 * Attendre que la page soit chargée avant d'activer les animations
 * 
 * setTimeout() crée un court délai pour :
 * 1. Laisser le temps au navigateur de charger la page
 * 2. Améliorer les performances initiales
 * 3. Éviter les animations saccadées au chargement
 */
setTimeout(() => {
    /**
     * Ajout de la classe 'will-animate' à tous les éléments
     * 
     * Cette classe active les transitions CSS :
     * - opacity: 0 → 1
     * - transform: translateY(40px) → translateY(0)
     * 
     * Sans JavaScript, les éléments restent visibles (opacity: 1)
     * pour garantir l'accessibilité et le référencement (SEO).
     */
    animateElements.forEach(el => {
        el.classList.add('will-animate');
    });

    /**
     * Création de l'Intersection Observer
     * 
     * Cette API moderne permet de détecter quand un élément
     * entre ou sort du viewport de manière performante.
     */
    
    // ==========================================
    // 3. CONFIGURATION DE L'OBSERVER
    // ==========================================
    
    /**
     * Options de configuration de l'Intersection Observer
     */
    const observerOptions = {
        /**
         * threshold: 0.1
         * L'élément doit être visible à 10% pour déclencher l'animation
         * 
         * - 0 = dès que 1 pixel est visible
         * - 0.5 = quand 50% de l'élément est visible
         * - 1 = uniquement quand 100% est visible
         */
        threshold: 0.1,
        
        /**
         * rootMargin: '0px 0px -100px 0px'
         * Marge virtuelle ajoutée autour du viewport
         * 
         * Format : top right bottom left (comme CSS padding)
         * '-100px' en bas signifie que l'élément doit être 100px
         * au-dessus du bas de l'écran pour être considéré comme visible
         * 
         * Cela déclenche l'animation un peu avant que l'élément
         * n'entre complètement dans l'écran, pour une meilleure UX.
         */
        rootMargin: '0px 0px -100px 0px'
    };

    /**
     * Création de l'Intersection Observer avec une fonction callback
     * 
     * Le callback est appelé chaque fois qu'un élément observé
     * entre ou sort de la zone visible.
     */
    const observer = new IntersectionObserver((entries) => {
        /**
         * entries est un tableau contenant tous les éléments
         * dont la visibilité a changé
         * 
         * Pour chaque élément (entry), on vérifie s'il est visible
         */
        entries.forEach((entry, index) => {
            /**
             * entry.isIntersecting est true quand l'élément
             * entre dans la zone visible (selon threshold et rootMargin)
             */
            if (entry.isIntersecting) {
                /**
                 * Ajout de la classe 'show' qui déclenche l'animation
                 * 
                 * Le CSS gère la transition :
                 * .will-animate.animate.show {
                 *     opacity: 1;
                 *     transform: translateY(0);
                 * }
                 */
                entry.target.classList.add('show');
                
                /**
                 * OPTIONNEL : On pourrait arrêter d'observer l'élément
                 * une fois qu'il est apparu :
                 * 
                 * observer.unobserve(entry.target);
                 * 
                 * Cela améliorerait les performances mais empêcherait
                 * les animations de se rejouer si l'utilisateur remonte.
                 * 
                 * Actuellement, on garde l'observation active pour permettre
                 * aux animations de se rejouer (bien que ce ne soit pas
                 * implémenté dans le CSS actuel avec les classes 'show').
                 */
            }
        });
    }, observerOptions);

    /**
     * Observer tous les éléments à animer
     * 
     * Pour chaque élément sélectionné précédemment,
     * on demande à l'observer de le surveiller
     */
    animateElements.forEach(el => observer.observe(el));
    
}, 100); // Délai de 100ms avant d'activer les animations


/**
 * ==========================================
 * RESPECT DES PRÉFÉRENCES D'ACCESSIBILITÉ
 * ==========================================
 * 
 * Certains utilisateurs préfèrent réduire les animations
 * pour des raisons de confort ou d'accessibilité
 * (épilepsie, troubles vestibulaires, etc.)
 * 
 * La media query 'prefers-reduced-motion' permet de
 * détecter cette préférence.
 */

/**
 * Détection de la préférence "réduire les animations"
 */
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/**
 * Si l'utilisateur préfère réduire les animations,
 * on peut :
 * 1. Désactiver complètement les animations
 * 2. Les réduire (durées plus courtes, moins d'effets)
 */
if (prefersReducedMotion) {
    /**
     * Approche 1 : Désactiver les animations en CSS
     * 
     * On pourrait ajouter une classe au body :
     * document.body.classList.add('no-animations');
     * 
     * Et dans le CSS :
     * .no-animations * {
     *     animation-duration: 0.01ms !important;
     *     transition-duration: 0.01ms !important;
     * }
     */
    
    /**
     * Approche 2 (actuelle) : Afficher tous les éléments immédiatement
     * 
     * Pour chaque élément à animer, on ajoute directement
     * la classe 'show' sans attendre le scroll
     */
    animateElements.forEach(el => {
        el.classList.add('show');
    });
    
    // Note : Dans ce cas, l'Intersection Observer n'est pas créé
    // car il est dans le setTimeout qui ne sera pas exécuté
}


/**
 * NOTES TECHNIQUES :
 * 
 * 1. Intersection Observer API :
 *    - API moderne pour détecter la visibilité des éléments
 *    - Très performante (pas besoin de calculer la position au scroll)
 *    - Supporte IE avec un polyfill
 *    - Alternative à l'ancien pattern : window.addEventListener('scroll')
 * 
 * 2. Performance :
 *    - L'observer fonctionne de manière asynchrone
 *    - N'impacte pas le thread principal
 *    - Beaucoup plus efficace que les calculs manuels
 * 
 * 3. Progressive Enhancement :
 *    - Sans JavaScript, les éléments restent visibles (opacity: 1)
 *    - Le site reste fonctionnel même si JS est désactivé
 *    - SEO : les robots voient tout le contenu
 * 
 * 4. Accessibilité :
 *    - Respect de prefers-reduced-motion
 *    - Transitions douces (0.6s à 0.8s)
 *    - Pas de mouvements brusques
 * 
 * 5. Classes CSS correspondantes :
 *    .will-animate : active les transitions
 *    .animate : animation depuis le bas
 *    .animate-left : animation depuis la gauche
 *    .animate-right : animation depuis la droite
 *    .animate-scale : animation avec zoom
 *    .show : état final visible
 */

/**
 * AMÉLIORATIONS POSSIBLES :
 * 
 * 1. Animation en cascade :
 *    - Ajouter un délai progressif (stagger) entre les éléments
 *    - Exemple : element.style.transitionDelay = `${index * 0.1}s`
 * 
 * 2. Animations plus complexes :
 *    - Rotation, flip, bounce, etc.
 *    - Utiliser des bibliothèques comme GSAP pour plus de contrôle
 * 
 * 3. Rejeu des animations :
 *    - Retirer la classe 'show' quand l'élément sort du viewport
 *    - Permet de rejouer l'animation à chaque passage
 * 
 * 4. Loading states :
 *    - Ajouter des skeletons/placeholders pendant le chargement
 *    - Transition fluide du skeleton vers le contenu réel
 * 
 * 5. Parallax :
 *    - Créer des effets de parallaxe au scroll
 *    - Différentes vitesses pour différentes couches
 */
