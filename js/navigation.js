/* ==========================================
   GESTION DE LA NAVIGATION
   ==========================================
   
   Ce script gère les interactions liées à la
   navigation du site :
   - Menu mobile (hamburger)
   - Scroll fluide vers les sections
   - Effet de l'en-tête au scroll
   
   Fonctionnalités :
   - Toggle du menu mobile
   - Smooth scroll vers les ancres
   - Ajout d'une classe au header lors du scroll
   - Fermeture automatique du menu après clic
   ========================================== */


// ==========================================
// 1. MENU MOBILE (HAMBURGER)
// ==========================================

/**
 * Sélection des éléments nécessaires au menu mobile
 */
const mobileBtn = document.querySelector('.mobile-menu-btn');  // Bouton hamburger (☰)
const navLinks = document.querySelector('.nav-links');          // Menu de navigation
const backdrop = document.querySelector('.nav-backdrop');       // Fond sombre derrière le menu

/**
 * Fonction pour basculer l'état du menu mobile
 * 
 * Cette fonction :
 * - Ouvre/ferme le menu latéral
 * - Affiche/cache le fond sombre
 * - Change l'icône du bouton (☰ → ✕)
 * - Empêche le scroll du body quand le menu est ouvert
 */
function toggleMenu() {
    // toggle() ajoute la classe si elle n'existe pas, la retire sinon
    navLinks.classList.toggle('active');
    backdrop.classList.toggle('active');
    
    // Change l'icône du bouton selon l'état du menu
    // Si le menu a la classe 'active', affiche ✕, sinon affiche ☰
    mobileBtn.textContent = navLinks.classList.contains('active') ? '✕' : '☰';
    
    // Gestion du scroll du body
    // Si le menu est ouvert (active), empêche le scroll de la page
    // overflow: 'hidden' cache la scrollbar et empêche le défilement
    // '' restaure la valeur par défaut (permet le scroll)
    document.body.style.overflow = navLinks.classList.contains('active') ? 'hidden' : '';
}

/**
 * Écouteurs d'événements pour le menu mobile
 */

// Clic sur le bouton hamburger
mobileBtn.addEventListener('click', toggleMenu);

// Clic sur le fond sombre (backdrop)
// Permet de fermer le menu en cliquant à côté
backdrop.addEventListener('click', toggleMenu);


// ==========================================
// 2. SMOOTH SCROLL (DÉFILEMENT FLUIDE)
// ==========================================

/**
 * Gestion du défilement fluide vers les sections
 * 
 * Lorsqu'un utilisateur clique sur un lien d'ancre
 * (href="#section"), au lieu d'un saut brusque,
 * on crée un défilement animé et fluide.
 */

// Sélectionne tous les liens qui commencent par "#"
// querySelectorAll() retourne une NodeList (similaire à un tableau)
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    // Pour chaque lien d'ancre, ajoute un écouteur d'événement
    anchor.addEventListener('click', function (e) {
        // Récupère la valeur de l'attribut href
        const href = this.getAttribute('href');
        
        // Si le href est juste "#" (lien vers le haut de page),
        // on sort de la fonction (return) sans rien faire
        if (href === '#') return;
        
        // Empêche le comportement par défaut du navigateur
        // (qui serait de sauter directement à la section)
        e.preventDefault();
        
        // Trouve l'élément cible grâce à son ID
        // Par exemple, si href="#services", cherche l'élément avec id="services"
        const target = document.querySelector(href);
        
        // Si l'élément cible existe
        if (target) {
            // Récupère la hauteur du header fixe
            // offsetHeight donne la hauteur totale de l'élément en pixels
            const headerHeight = document.querySelector('header').offsetHeight;
            
            // Calcule la position de défilement
            // getBoundingClientRect().top : distance entre le haut de l'élément et le haut de la fenêtre
            // window.pageYOffset : position actuelle du scroll
            // - headerHeight : soustrait la hauteur du header pour que la section ne soit pas cachée dessous
            const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight;
            
            // Effectue le défilement animé
            window.scrollTo({
                top: targetPosition,        // Position de destination
                behavior: 'smooth'          // Animation fluide (au lieu d'un saut instantané)
            });
            
            // Si le menu mobile est ouvert, le ferme après le clic
            if (navLinks.classList.contains('active')) {
                toggleMenu();
            }
        }
    });
});


// ==========================================
// 3. EFFET DE L'EN-TÊTE AU SCROLL
// ==========================================

/**
 * Ajoute une classe au header lors du défilement
 * pour créer un effet visuel (ombre, changement de couleur, etc.)
 */

// Sélectionne l'élément header
const header = document.querySelector('header');

/**
 * Écouteur d'événement sur le scroll de la fenêtre
 * 
 * window.addEventListener('scroll', ...) se déclenche
 * à chaque fois que l'utilisateur fait défiler la page
 */
window.addEventListener('scroll', () => {
    // Vérifie si l'utilisateur a scrollé de plus de 100 pixels
    // window.pageYOffset donne la position actuelle du scroll vertical
    const scrolled = window.pageYOffset > 100;
    
    // toggle() avec un deuxième paramètre force l'ajout (true) ou le retrait (false) de la classe
    // Si scrolled est true, ajoute la classe 'scrolled'
    // Si scrolled est false, retire la classe 'scrolled'
    header.classList.toggle('scrolled', scrolled);
});


/**
 * NOTES TECHNIQUES :
 * 
 * 1. classList :
 *    - Méthode moderne pour manipuler les classes CSS
 *    - .add() : ajoute une classe
 *    - .remove() : retire une classe
 *    - .toggle() : bascule (ajoute si absente, retire si présente)
 *    - .contains() : vérifie si la classe existe
 * 
 * 2. Event listeners :
 *    - addEventListener() attache une fonction à un événement
 *    - Événements courants : 'click', 'scroll', 'resize', 'keydown', etc.
 *    - Permet plusieurs écouteurs sur le même événement
 *    - Plus moderne que onclick=""
 * 
 * 3. querySelector vs querySelectorAll :
 *    - querySelector() : retourne le premier élément trouvé
 *    - querySelectorAll() : retourne tous les éléments (NodeList)
 *    - Acceptent les sélecteurs CSS (classes, IDs, attributs, etc.)
 * 
 * 4. getBoundingClientRect() :
 *    - Retourne la taille et position d'un élément
 *    - Propriétés : top, right, bottom, left, width, height
 *    - Utile pour les calculs de position et d'animation
 * 
 * 5. window.scrollTo() :
 *    - Fait défiler la page vers une position
 *    - behavior: 'smooth' crée une animation fluide
 *    - Supporté par tous les navigateurs modernes
 * 
 * 6. Performance :
 *    - L'événement 'scroll' peut se déclencher très fréquemment
 *    - Pour de meilleures performances, on pourrait utiliser
 *      un "throttle" ou "debounce" pour limiter les exécutions
 *    - Dans ce cas, le code est simple donc les performances restent bonnes
 */

/**
 * AMÉLIORATIONS POSSIBLES :
 * 
 * 1. Accessibilité :
 *    - Ajouter la gestion du clavier (touche Escape pour fermer le menu)
 *    - Gérer le focus dans le menu mobile
 *    - Ajouter des attributs ARIA (aria-expanded, aria-controls)
 * 
 * 2. Performance :
 *    - Utiliser IntersectionObserver pour détecter les sections visibles
 *    - Mettre en surbrillance le lien de navigation de la section actuelle
 * 
 * 3. UX :
 *    - Ajouter une animation de fermeture du menu après un délai
 *    - Détecter le swipe (glissement) pour fermer le menu
 */
