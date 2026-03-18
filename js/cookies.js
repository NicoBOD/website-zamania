/* ==========================================
   GESTION DE LA BANNIÈRE DE COOKIES
   ==========================================
   
   Ce script gère l'affichage et les interactions
   avec la bannière de consentement aux cookies.
   
   Fonctionnalités :
   - Affichage conditionnel de la bannière
   - Gestion des boutons Accepter/Refuser
   - Sauvegarde du consentement
   - Respect de la vie privée
   ========================================== */


// Sélection des éléments du DOM
const cookieBanner = document.getElementById('cookieBanner');      // La bannière elle-même
const acceptCookies = document.getElementById('acceptCookies');    // Bouton "Accepter"
const declineCookies = document.getElementById('declineCookies');  // Bouton "Refuser"

/**
 * Vérification du consentement existant
 * 
 * Vérifie si l'utilisateur a déjà fait un choix
 * concernant les cookies lors d'une visite précédente.
 */

// Récupère la valeur stockée dans localStorage
// localStorage.getItem() retourne null si la clé n'existe pas
const cookieConsent = localStorage.getItem('cookieConsent');

/**
 * Affichage conditionnel de la bannière
 * 
 * Si aucun consentement n'a été enregistré,
 * affiche la bannière après un court délai
 * pour ne pas perturber l'expérience initiale.
 */
if (!cookieConsent) {
    // setTimeout() exécute une fonction après un délai (en millisecondes)
    // 1000 ms = 1 seconde
    setTimeout(() => {
        // Ajoute la classe 'show' qui déclenche l'animation d'apparition
        // (définie dans le CSS avec transform: translateY(0))
        cookieBanner.classList.add('show');
    }, 1000);
}

/**
 * Gestion du bouton "Accepter"
 * 
 * Lorsque l'utilisateur clique sur "Accepter" :
 * 1. Enregistre le consentement
 * 2. Masque la bannière
 */
acceptCookies.addEventListener('click', () => {
    // Enregistre le consentement dans localStorage
    // La valeur 'accepted' permet de distinguer acceptation et refus
    localStorage.setItem('cookieConsent', 'accepted');
    
    // Masque la bannière en retirant la classe 'show'
    // L'animation CSS (transform: translateY(100%)) fait glisser la bannière vers le bas
    cookieBanner.classList.remove('show');
    
    // Note : Dans une application réelle, c'est ici que vous
    // activeriez les cookies tiers (analytics, publicité, etc.)
    // Exemple : activerGoogleAnalytics();
});

/**
 * Gestion du bouton "Refuser"
 * 
 * Lorsque l'utilisateur clique sur "Refuser" :
 * 1. Enregistre le refus
 * 2. Supprime la préférence de thème (par respect de la vie privée)
 * 3. Masque la bannière
 */
declineCookies.addEventListener('click', () => {
    // Enregistre le refus dans localStorage
    localStorage.setItem('cookieConsent', 'declined');
    
    // Par respect de la vie privée, si l'utilisateur refuse les cookies,
    // on supprime également la préférence de thème stockée
    // localStorage.removeItem() supprime une entrée du stockage
    localStorage.removeItem('theme');
    
    // Masque la bannière
    cookieBanner.classList.remove('show');
    
    // Note : Dans une application réelle, vous devriez :
    // - Désactiver tous les cookies non essentiels
    // - Informer les services tiers du refus
    // - Respecter le choix pour les prochaines visites
});

/**
 * NOTES SUR LE RGPD ET LES COOKIES :
 * 
 * 1. Types de cookies :
 *    - Essentiels : Nécessaires au fonctionnement (pas de consentement requis)
 *    - Fonctionnels : Amélioration de l'expérience (consentement requis)
 *    - Analytics : Statistiques d'utilisation (consentement requis)
 *    - Marketing : Publicité ciblée (consentement requis)
 * 
 * 2. Obligations légales (RGPD) :
 *    - Informer clairement l'utilisateur
 *    - Obtenir le consentement avant de déposer des cookies non essentiels
 *    - Permettre de refuser aussi facilement que d'accepter
 *    - Permettre de retirer son consentement
 *    - Conserver la preuve du consentement
 * 
 * 3. Bonnes pratiques :
 *    - Ne pas bloquer l'accès au site si l'utilisateur refuse
 *    - Respecter le choix de l'utilisateur
 *    - Offrir un moyen de modifier les préférences
 *    - Être transparent sur l'utilisation des données
 * 
 * 4. localStorage vs Cookies :
 *    - localStorage : Stockage local, non envoyé au serveur
 *    - Cookies : Envoyés avec chaque requête HTTP
 *    - Pour le RGPD, les deux nécessitent un consentement si non essentiels
 * 
 * 5. Implémentation actuelle :
 *    - Ce site utilise uniquement localStorage pour la préférence de thème
 *    - C'est un cookie "fonctionnel" qui améliore l'expérience
 *    - Si refusé, la préférence de thème est supprimée
 *    - Aucune donnée n'est envoyée à des tiers
 */

/**
 * AMÉLIORATION POSSIBLE :
 * 
 * Pour une conformité totale au RGPD, vous pourriez ajouter :
 * 
 * 1. Un bouton "Paramétrer" pour choisir quels cookies accepter
 * 2. Une page dédiée à la politique de confidentialité
 * 3. Une durée d'expiration du consentement (ex: 13 mois)
 * 4. Un moyen de modifier les préférences après le premier choix
 * 5. Des identifiants uniques pour tracer le consentement
 */
