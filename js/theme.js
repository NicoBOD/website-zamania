/* ==========================================
   GESTION DU THÈME (DÉFAUT : SOMBRE)
   ==========================================
   
   Ce script gère le basculement entre le mode
   clair et le mode sombre. 
   
   PARTICULARITÉ : Le site est en mode SOMBRE
   par défaut (imposé par le HTML). Ce script
   vérifie si l'utilisateur a précédemment
   demandé le mode CLAIR pour restaurer son choix.
   
   Fonctionnalités :
   - Mode sombre par défaut (sans flash)
   - Restauration du mode clair si sauvegardé
   - Mise à jour de l'icône du bouton
   - Sauvegarde du choix utilisateur
   ========================================== */


// Sélection des éléments du DOM nécessaires
const themeToggle = document.getElementById('themeToggle');  // Bouton de bascule
const themeIcon = document.querySelector('.theme-toggle-icon');  // Icône (☀️ ou 🌙)
const html = document.documentElement;  // Élément <html> qui porte l'attribut data-theme

/**
 * Initialisation du thème au chargement
 * * Logique de priorité modifiée pour le "Dark Mode First" :
 * 1. Si une préférence "light" est sauvegardée -> On passe en clair.
 * 2. Sinon (aucune préférence ou "dark") -> On reste en sombre (défaut HTML).
 */

// Vérifie si l'utilisateur a déjà choisi un thème (stocké dans localStorage)
const savedTheme = localStorage.getItem('theme');

// Application de la logique inversée
if (savedTheme === 'light') {
    // L'utilisateur veut explicitement du clair
    // On retire l'attribut mis par défaut dans le HTML
    html.removeAttribute('data-theme');
    updateThemeIcon('light');
} else {
    // Par défaut (nouvelle visite) OU si "dark" est sauvegardé
    // On s'assure que l'attribut est présent (sécurité)
    html.setAttribute('data-theme', 'dark');
    updateThemeIcon('dark');
}

/**
 * Gestion du clic sur le bouton de bascule
 * * Inverse le thème actuel et sauvegarde le choix
 */
themeToggle.addEventListener('click', () => {
    // Vérifie si on est actuellement en mode sombre
    // (La présence de l'attribut signifie mode sombre)
    const isDark = html.getAttribute('data-theme') === 'dark';
    
    if (isDark) {
        // --- PASSAGE AU MODE CLAIR ---
        
        // On retire l'attribut pour utiliser les variables CSS racines (:root)
        html.removeAttribute('data-theme');
        
        // On sauvegarde la préférence "light"
        localStorage.setItem('theme', 'light');
        
        // Mise à jour de l'icône
        updateThemeIcon('light');
        
    } else {
        // --- PASSAGE AU MODE SOMBRE ---
        
        // On ajoute l'attribut pour activer les variables du dark-mode.css
        html.setAttribute('data-theme', 'dark');
        
        // On sauvegarde la préférence "dark"
        localStorage.setItem('theme', 'dark');
        
        // Mise à jour de l'icône
        updateThemeIcon('dark');
    }
});

/**
 * Met à jour l'icône du bouton selon le thème
 * * @param {string} theme - 'light' ou 'dark'
 * * Affiche ☀️ en mode clair et 🌙 en mode sombre
 */
function updateThemeIcon(theme) {
    // Opérateur ternaire : condition ? valeur_si_vrai : valeur_si_faux
    themeIcon.textContent = theme === 'light' ? '☀️' : '🌙';
}

/**
 * NOTE SUR LA DÉTECTION SYSTÈME :
 * * Dans cette version "Imposed Dark Mode", nous avons retiré
 * l'écouteur d'événement système (window.matchMedia).
 * * Raison : Nous voulons que l'identité visuelle du site soit
 * sombre par défaut pour tout le monde, indépendamment du
 * réglage de leur système d'exploitation, sauf si l'utilisateur
 * décide manuellement de cliquer sur le bouton.
 */

/**
 * NOTES TECHNIQUES :
 * * 1. localStorage :
 * - Stockage persistant dans le navigateur
 * - Permet de se souvenir si l'utilisateur a cliqué sur le soleil
 * * 2. data-theme :
 * - Présent = Mode Sombre (chargé par défaut dans le HTML)
 * - Absent = Mode Clair (design par défaut du CSS styles.css)
 * * 3. Performance :
 * - Comme l'attribut est déjà dans le HTML, il n'y a aucun
 * "FOUC" (Flash of Unstyled Content) ou flash blanc au chargement.
 */