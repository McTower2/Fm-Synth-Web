    // Configurazione ID
    const RELEASE_KNOB_ID = 'envrelease';
    const CANVAS_ID = 'envelopeCanvas';

    function drawReleaseEnvelope() {
        const knob = document.getElementById(RELEASE_KNOB_ID);
        const canvas = document.getElementById(CANVAS_ID);

        // Controllo di sicurezza: se gli oggetti non esistono, fermati
        if (!knob || !canvas) {
            console.warn("Canvas o Knob non trovati. Controlla gli ID.");
            return;
        }

        const ctx = canvas.getContext('2d');
        const w = canvas.width;
        const h = canvas.height;

        // --- 1. PULIZIA E STILE NEON ---
        ctx.clearRect(0, 0, w, h);

        const neonColor = '#d900ff'; 
        ctx.strokeStyle = neonColor;
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.shadowBlur = 15;
        ctx.shadowColor = neonColor;

        // Margini (Padding)
        const padTop = 5;
        const padBot = 5;

        // --- 2. NORMALIZZAZIONE DEL VALORE (Cruciale) ---
        // Leggiamo i limiti impostati nell'HTML della manopola (default 0 e 100 se non specificati)
        let min = parseFloat(knob.getAttribute('min')) || 0;
        let max = parseFloat(knob.getAttribute('max')) || 100;
        let current = parseFloat(knob.value);

        // Protezione matematica
        if (isNaN(current)) current = min;
        
        // Calcolo valore normalizzato da 0.0 a 1.0
        // (current - min) / (max - min)
        let range = max - min;
        if (range <= 0) range = 1; // Evita divisione per zero
        
        let norm = (current - min) / range;
        
        // Clamp: Assicuriamoci che stia tra 0 e 1
        if (norm < 0) norm = 0;
        if (norm > 1) norm = 1;

        // --- 3. CALCOLO FATTORE DI DECADIMENTO ---
        // Vogliamo: 
        // Norm 0 (Minimo) -> Decadimento veloce -> Fattore ALTO (es. 15)
        // Norm 1 (Massimo) -> Decadimento lento  -> Fattore BASSO (es. 0.2)
        
        // Formula: Partiamo da un decadimento veloce (15) e sottraiamo in base alla manopola
        // Usiamo (1 - norm) così che quando norm è 1, il fattore è piccolo.
        // Eleviamo al quadrato (Math.pow) per rendere la sensibilità della manopola più naturale (logaritmica).
        const decayFactor = 0.5 + (15 * Math.pow((1 - norm), 2)); 

        // --- 4. DISEGNO ---
        ctx.beginPath();

        // A) Asticella Verticale (Attacco Istantaneo)
        // Dal basso (Time 0, Amp 0)
        ctx.moveTo(2, h - padBot); 
        // All'alto (Time 0, Amp 1)
        ctx.lineTo(2, padTop);

        // B) Curva di Release
        // Disegniamo pixel per pixel
        for (let x = 2; x <= w; x++) {
            // Normalizziamo la X da 0 a 1 rispetto alla larghezza del canvas
            let xProgress = (x - 2) / (w - 2); 

            // Formula Esponenziale: y = e^(-k * x)
            let amplitude = Math.exp(-decayFactor * xProgress * 3); // *3 serve a scalare la curva nello schermo

            // Mappiamo l'ampiezza (0..1) sulle coordinate Y del canvas (Top..Bottom)
            // Y alto = padTop
            // Y basso = h - padBot
            let drawHeight = h - padTop - padBot;
            let y = padTop + ((1 - amplitude) * drawHeight);

            ctx.lineTo(x, y);
        }

        ctx.stroke();
    }

    // --- 5. ATTIVAZIONE ---
    window.addEventListener('load', () => {
        const knob = document.getElementById(RELEASE_KNOB_ID);
        if (knob) {
            // Disegna subito appena la pagina è pronta
            drawReleaseEnvelope();
            // Disegna ogni volta che muovi la manopola
            knob.addEventListener('input', drawReleaseEnvelope);
        }
    });