document.addEventListener("DOMContentLoaded", function () {
    const canvases = document.querySelectorAll(".particle-network-canvas");

    canvases.forEach(canvas => {
        initNetworkAnimation(canvas);
    });
});

function initNetworkAnimation(canvas) {
    const ctx = canvas.getContext("2d");
    const section = canvas.parentElement;

    let particlesArray;
    let width, height;
    
    // Variables de configuration
    let connectionDistance; 
    const mouseRadius = 150;
    const gridSpacing = 60;
    const gridRevealRadius = 200;

    // Variable pour stocker la couleur actuelle
    let particleColorRGB = "255, 255, 255"; // Valeur par défaut

    let mouse = {
        x: null,
        y: null,
        radius: mouseRadius
    };

    // --- GESTION COULEUR DYNAMIQUE ---
    
    // Fonction pour lire la variable CSS
    function updateColor() {
        const style = getComputedStyle(section);
        const colorVar = style.getPropertyValue('--particle-rgb').trim();
        // Si la variable est trouvée dans le CSS, on l'utilise, sinon blanc
        if (colorVar) {
            particleColorRGB = colorVar;
        }
    }

    // --- GESTION SOURIS & TACTILE ---

    function updateInputPosition(clientX, clientY) {
        const rect = canvas.getBoundingClientRect();
        mouse.x = clientX - rect.left;
        mouse.y = clientY - rect.top;
    }

    section.addEventListener("mousemove", function (event) {
        updateInputPosition(event.clientX, event.clientY);
    });

    section.addEventListener("mouseleave", function () {
        mouse.x = null;
        mouse.y = null;
    });

    section.addEventListener("touchstart", function (event) {
        if(event.touches.length > 0) {
            updateInputPosition(event.touches[0].clientX, event.touches[0].clientY);
        }
    }, {passive: true});

    section.addEventListener("touchmove", function (event) {
        if(event.touches.length > 0) {
            updateInputPosition(event.touches[0].clientX, event.touches[0].clientY);
        }
    }, {passive: true});

    section.addEventListener("touchend", function () {
        mouse.x = null;
        mouse.y = null;
    });

    // --- REDIMENSIONNEMENT ---

    function resizeCanvas() {
        width = section.offsetWidth;
        height = section.offsetHeight;

        const dpr = window.devicePixelRatio || 1;
        
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        canvas.style.width = width + "px";
        canvas.style.height = height + "px";

        ctx.scale(dpr, dpr);

        if (width < 768) {
            connectionDistance = 80;
        } else {
            connectionDistance = 120;
        }
        
        // On met à jour la couleur au resize (utile au chargement)
        updateColor();
        initParticles();
    }
    
    window.addEventListener("resize", resizeCanvas);

    // --- DESSIN GRILLE ---

    function drawGrid() {
        if (mouse.x === null || mouse.y === null) return;

        ctx.beginPath();
        const gradient = ctx.createRadialGradient(mouse.x, mouse.y, 0, mouse.x, mouse.y, gridRevealRadius);
        
        // Utilisation de la couleur dynamique pour la grille
        gradient.addColorStop(0, `rgba(${particleColorRGB}, 0.25)`);
        gradient.addColorStop(1, `rgba(${particleColorRGB}, 0)`);

        ctx.strokeStyle = gradient;
        ctx.lineWidth = 1;

        for (let x = 0; x <= width + gridSpacing; x += gridSpacing) {
            let alignedX = x - (x % gridSpacing);
            ctx.moveTo(alignedX, 0);
            ctx.lineTo(alignedX, height);
        }

        for (let y = 0; y <= height + gridSpacing; y += gridSpacing) {
             let alignedY = y - (y % gridSpacing);
            ctx.moveTo(0, alignedY);
            ctx.lineTo(width, alignedY);
        }

        ctx.stroke();
        ctx.closePath();
    }

    // --- PARTICULES ---

    class Particle {
        constructor(x, y, directionX, directionY, size) {
            this.x = x;
            this.y = y;
            this.directionX = directionX;
            this.directionY = directionY;
            this.size = size;
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2, false);
            // Utilisation de la couleur dynamique pour les points
            ctx.fillStyle = `rgba(${particleColorRGB}, 0.6)`;
            ctx.fill();
        }

        update() {
            if (this.x > width || this.x < 0) this.directionX = -this.directionX;
            if (this.y > height || this.y < 0) this.directionY = -this.directionY;

            this.x += this.directionX;
            this.y += this.directionY;

            if (mouse.x != null) {
                let dx = mouse.x - this.x;
                let dy = mouse.y - this.y;
                let distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < mouse.radius + this.size) {
                    if (mouse.x < this.x && this.x < width - this.size * 10) this.x += 2;
                    if (mouse.x > this.x && this.x > this.size * 10) this.x -= 2;
                    if (mouse.y < this.y && this.y < height - this.size * 10) this.y += 2;
                    if (mouse.y > this.y && this.y > this.size * 10) this.y -= 2;
                }
            }
            this.draw();
        }
    }

    function initParticles() {
        particlesArray = [];
        const divider = width < 768 ? 18000 : 12000;
        const numberOfParticles = (width * height) / divider;

        for (let i = 0; i < numberOfParticles; i++) {
            let size = (Math.random() * 2) + 1;
            let x = (Math.random() * ((width - size * 2) - (size * 2)) + size * 2);
            let y = (Math.random() * ((height - size * 2) - (size * 2)) + size * 2);
            let directionX = (Math.random() * 1) - 0.5;
            let directionY = (Math.random() * 1) - 0.5;

            particlesArray.push(new Particle(x, y, directionX, directionY, size));
        }
    }

    function connect() {
        let opacityValue = 1;
        for (let a = 0; a < particlesArray.length; a++) {
            for (let b = a; b < particlesArray.length; b++) {
                let dx = particlesArray[a].x - particlesArray[b].x;
                let dy = particlesArray[a].y - particlesArray[b].y;
                let distance = dx * dx + dy * dy;

                if (distance < (connectionDistance * connectionDistance)) {
                    opacityValue = 1 - (distance / (connectionDistance * connectionDistance));
                    // Utilisation de la couleur dynamique pour les lignes
                    ctx.strokeStyle = `rgba(${particleColorRGB}, ${opacityValue * 0.2})`;
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(particlesArray[a].x, particlesArray[a].y);
                    ctx.lineTo(particlesArray[b].x, particlesArray[b].y);
                    ctx.stroke();
                }
            }
            
             if(mouse.x != null) {
                 let dx = particlesArray[a].x - mouse.x;
                 let dy = particlesArray[a].y - mouse.y;
                 let distanceMouse = dx * dx + dy * dy;
                
                if (distanceMouse < (mouse.radius * mouse.radius)) {
                     // Ligne vers la souris
                     ctx.strokeStyle = `rgba(${particleColorRGB}, 0.3)`;
                     ctx.beginPath();
                     ctx.moveTo(particlesArray[a].x, particlesArray[a].y);
                     ctx.lineTo(mouse.x, mouse.y);
                     ctx.stroke();
                }
            }
        }
    }

    function animate() {
        requestAnimationFrame(animate);
        
        // On vérifie la couleur à chaque frame pour gérer le changement de thème instantané
        // (Léger sur la performance car on lit juste une variable)
        updateColor();
        
        ctx.clearRect(0, 0, width, height);
        drawGrid();
        for (let i = 0; i < particlesArray.length; i++) {
            particlesArray[i].update();
        }
        connect();
    }

    // Lancement
    resizeCanvas();
    animate();
}