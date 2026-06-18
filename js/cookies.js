/* ==========================================
   BANDEAU D'INFORMATION (sans cookie)
   ==========================================

   Le site ne dépose AUCUN cookie de suivi : il n'y a donc pas de
   consentement à recueillir. Ce bandeau informe simplement le visiteur,
   une seule fois, de la nature des données utilisées :
     - une préférence d'affichage (thème) conservée en localStorage ;
     - une mesure d'audience anonyme, sans cookie (GoatCounter).

   Le fait d'avoir vu le bandeau est mémorisé dans localStorage
   ('cookieConsent') afin de ne pas le réafficher — y compris aux
   visiteurs ayant déjà répondu à l'ancienne version (Accepter/Refuser).
   ========================================== */

const noticeBanner = document.getElementById('cookieBanner');
const acknowledgeNotice = document.getElementById('acknowledgeNotice');

// Affiche le bandeau après un court délai, seulement s'il n'a jamais été vu.
if (noticeBanner && !localStorage.getItem('cookieConsent')) {
    setTimeout(() => {
        noticeBanner.classList.add('show');
    }, 1000);
}

// « J'ai compris » : mémorise et masque le bandeau (aucune autre action).
if (acknowledgeNotice && noticeBanner) {
    acknowledgeNotice.addEventListener('click', () => {
        localStorage.setItem('cookieConsent', 'acknowledged');
        noticeBanner.classList.remove('show');
    });
}
