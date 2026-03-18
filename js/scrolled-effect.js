  window.addEventListener('scroll', function() {
    const header = document.querySelector('header');
    // Si on descend de plus de 50px, on ajoute la classe "scrolled"
    if (window.scrollY > 50) {
      header.classList.add('scrolled');
    } else {
      // Sinon, on l'enlève pour revenir à l'état initial
      header.classList.remove('scrolled');
    }
  });
