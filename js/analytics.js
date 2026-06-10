/* ==========================================
   STATISTIQUES DE VISITE (sans cookie)
   ==========================================
   GoatCounter : mesure d'audience respectueuse de la vie privée
   (pas de cookie, pas de données personnelles, conforme RGPD,
   aucun bandeau de consentement requis).

   Tant que GOATCOUNTER est vide, AUCUNE requête n'est émise.

   Activation (2 minutes) :
     1. créer un compte gratuit sur https://www.goatcounter.com
        avec le code « zamania » ;
     2. renseigner ci-dessous :
        const GOATCOUNTER = 'https://zamania.goatcounter.com/count';
   ========================================== */

const GOATCOUNTER = 'https://zamania.goatcounter.com/count';

(function () {
    'use strict';
    if (!GOATCOUNTER) return;

    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://gc.zgo.at/count.js';
    script.dataset.goatcounter = GOATCOUNTER;
    document.head.appendChild(script);
})();
