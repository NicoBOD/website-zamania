/* ==========================================
   FORMULAIRE DE CONTACT
   ==========================================
   Envoi du formulaire statique vers un service compatible
   (Formspree, Web3Forms...). Configuration en UNE ligne ci-dessous.

   Tant que FORM_ENDPOINT est vide, le bouton compose un e-mail
   (repli mailto) : le site reste fonctionnel sans configuration.

   Activation (5 minutes) :
     1. créer un formulaire sur https://formspree.io (gratuit) ;
     2. coller son URL ici, ex. : 'https://formspree.io/f/abcdwxyz'.
   ========================================== */

const FORM_ENDPOINT = 'https://formspree.io/f/xeewlejp';

(function () {
    'use strict';

    const form = document.querySelector('.contact-form');
    if (!form) return;

    const status = form.querySelector('.form-status');
    const submit = form.querySelector('button[type="submit"]');

    function show(kind, message) {
        status.className = 'form-status ' + kind;
        status.textContent = message;
    }

    function mailtoFallback(fields) {
        const subject = form.dataset.mailSubject || 'Contact';
        const lines = [];
        lines.push((form.dataset.labelName || 'Nom') + ' : ' + fields.get('name'));
        if (fields.get('company')) {
            lines.push((form.dataset.labelCompany || 'Société') + ' : ' + fields.get('company'));
        }
        lines.push('');
        lines.push(fields.get('message'));
        window.location.href = 'mailto:contact@zamania.fr'
            + '?subject=' + encodeURIComponent(subject)
            + '&body=' + encodeURIComponent(lines.join('\n'));
    }

    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        if (!form.reportValidity()) return;

        const fields = new FormData(form);
        if (fields.get('_gotcha')) return;          /* robot pris au piège */

        if (!FORM_ENDPOINT) {
            mailtoFallback(fields);
            return;
        }

        submit.disabled = true;
        show('', '…');
        try {
            const response = await fetch(FORM_ENDPOINT, {
                method: 'POST',
                body: fields,
                headers: { 'Accept': 'application/json' }
            });
            if (!response.ok) throw new Error('HTTP ' + response.status);
            form.reset();
            show('success', form.dataset.success || 'OK');
        } catch (err) {
            show('error', form.dataset.error || 'Erreur');
        } finally {
            submit.disabled = false;
        }
    });
})();
