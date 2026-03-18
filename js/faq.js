/**
 * FAQ.JS - Gestion de l'accordéon FAQ
 * Permet d'ouvrir/fermer les réponses aux questions fréquentes
 */

// Attendre que le DOM soit complètement chargé
document.addEventListener('DOMContentLoaded', function() {
    // Sélectionner toutes les questions de la FAQ
    const faqQuestions = document.querySelectorAll('.faq-question');
    
    // Ajouter un écouteur d'événement à chaque question
    faqQuestions.forEach(question => {
        question.addEventListener('click', function() {
            // Récupérer la réponse associée (élément suivant)
            const answer = this.nextElementSibling;
            
            // Vérifier si la question est déjà ouverte
            const isOpen = this.getAttribute('aria-expanded') === 'true';
            
            // Fermer toutes les autres questions (optionnel - pour n'avoir qu'une question ouverte à la fois)
            // Décommenter les lignes suivantes si vous voulez ce comportement
            /*
            faqQuestions.forEach(otherQuestion => {
                if (otherQuestion !== this) {
                    otherQuestion.setAttribute('aria-expanded', 'false');
                    otherQuestion.nextElementSibling.classList.remove('active');
                }
            });
            */
            
            // Basculer l'état de la question actuelle
            if (isOpen) {
                // Fermer la réponse
                this.setAttribute('aria-expanded', 'false');
                answer.classList.remove('active');
            } else {
                // Ouvrir la réponse
                this.setAttribute('aria-expanded', 'true');
                answer.classList.add('active');
            }
        });
    });
    
    // Animation au scroll pour les éléments FAQ (utilise le système existant)
    // Les éléments avec la classe .animate apparaîtront progressivement
    // (géré par animations.js déjà existant)
});
