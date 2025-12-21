class ADSRVisualizer {
    // Aggiungiamo 'color' come argomento, con un default verde se non specificato
    constructor(suffix, color = '#00ff88') {
        this.suffix = suffix;
        this.color = color; // Salviamo il colore nell'istanza
        
        this.canvas = document.getElementById(`adsrCanvas_${suffix}`);
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        
        this.inputs = {
            a: document.getElementById(`attack_${suffix}`),
            d: document.getElementById(`decay_${suffix}`),
            s: document.getElementById(`sustain_${suffix}`),
            r: document.getElementById(`release_${suffix}`)
        };

        this.drawW = 0;
        this.drawH = 0;

        this.draw = this.draw.bind(this);
        this.resize = this.resize.bind(this);

        this.setupListeners();
        setTimeout(() => this.resize(), 50);
    }

    updateColor(newColor) {
        this.color = newColor;
        this.draw();
    }

// --- Helper: Converte Hex (#RRGGBB o #RRGGBBAA) in "r, g, b" ---
    hexToRgb(hex) {
        // 1. Rimuovi il cancelletto
        hex = hex.replace(/^#/, '');

        // 2. Se ci sono 8 cifre (RRGGBBAA), teniamo solo le prime 6 (RRGGBB)
        // Ignoriamo l'alpha finale perché lo gestiamo noi nel gradiente
        if (hex.length === 8) {
            hex = hex.substring(0, 6);
        }

        // 3. Parsing sicuro tramite substring
        // (Molto più sicuro dei bitwise operator su numeri grandi in JS)
        const bigint = parseInt(hex, 16);
        const r = (bigint >> 16) & 255;
        const g = (bigint >> 8) & 255;
        const b = bigint & 255;

        return `${r}, ${g}, ${b}`;
    }

    resize() {
        const rect = this.canvas.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return;

        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = rect.width * dpr;
        this.canvas.height = rect.height * dpr;
        this.ctx.scale(dpr, dpr);
        this.drawW = rect.width;
        this.drawH = rect.height;
        this.draw();
    }

    drawGrid() {
        const { ctx, drawW, drawH } = this;
        ctx.beginPath();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
        ctx.lineWidth = 1;
        for (let x = 0; x <= drawW; x += drawW / 10) { ctx.moveTo(x, 0); ctx.lineTo(x, drawH); }
        for (let y = 0; y <= drawH; y += drawH / 6) { ctx.moveTo(0, y); ctx.lineTo(drawW, y); }
        ctx.stroke();
    }

    getRatio(el) {
        if (!el) return 0;
        const val = parseFloat(el.value);
        const min = parseFloat(el.getAttribute('min')) || 0;
        const max = parseFloat(el.getAttribute('max')) || 100;
        return (val - min) / (max - min);
    }

    draw() {
        const { ctx, inputs, drawW: w, drawH: h, color } = this; // Estraiamo anche 'color'

        ctx.clearRect(0, 0, w, h);
        this.drawGrid();

        const rA = this.getRatio(inputs.a);
        const rD = this.getRatio(inputs.d);
        const rS = parseFloat(inputs.s.value);
        const rR = this.getRatio(inputs.r);

        const padding = 10;
        const graphW = w - (padding * 2);
        const graphH = h - (padding * 2);

        const maxSectionW = graphW * 0.45;
        const holdW = graphW * 0.16;

        const wA = rA * maxSectionW * 0.5;
        const wD = Math.max(rD * maxSectionW, 5);
        const wR = Math.max(rR * maxSectionW, 5);

        const x0 = padding;
        const xA = x0 + wA;
        const xD = xA + wD;
        const xS = xD + holdW;
        const xR = xS + wR;

        const yBase = h - padding;
        const yPeak = padding;
        const ySust = yBase - (rS * graphH);

        // --- Disegno Linea ---
        ctx.beginPath();
        ctx.moveTo(x0, yBase); // start point
        ctx.lineTo(xA, yPeak); // attack
        ctx.lineTo(xD, ySust); // decay
        ctx.lineTo(xS, ySust); // sustain
        ctx.lineTo(xR, yBase); // release

        ctx.lineJoin = 'round';
        ctx.lineCap = 'round';
        ctx.lineWidth = 3;
        
        // 1. Usa il colore dinamico per la linea
        ctx.strokeStyle = color; 
        
        // 2. Usa il colore dinamico per il glow (ombra)
        ctx.shadowBlur = 15;
        ctx.shadowColor = color;
        
        ctx.stroke();

        // --- Disegno Riempimento Sfumato ---
        ctx.shadowBlur = 0;
        ctx.lineTo(xR, h);
        ctx.lineTo(x0, h);
        ctx.closePath();

        // 3. Usa l'helper per creare i colori rgba del gradiente
        const rgb = this.hexToRgb(color);
        const grad = ctx.createLinearGradient(0, 0, 0, h);
        
        grad.addColorStop(0, `rgba(${rgb}, 0.4)`); // Opacità 0.4
        grad.addColorStop(1, `rgba(${rgb}, 0.0)`); // Opacità 0
        
        ctx.fillStyle = grad;
        ctx.fill();

        // 4. Pallini (restano bianchi o li vuoi colorati?)
        ctx.fillStyle = '#fff'; 
        [[xA, yPeak], [xD, ySust], [xS, ySust]].forEach(([dx, dy]) => {
            ctx.beginPath();
            ctx.arc(dx, dy, 2, 0, Math.PI * 2);
            ctx.fill();
        });
    }

    setupListeners() {
        Object.values(this.inputs).forEach(input => {
            if (input) {
                input.addEventListener('input', this.draw);
                input.addEventListener('change', this.draw);
            }
        });
    }
}

/////////////////////////////////////////////////
// LOGICA COLORI

let algorithmKnob = document.getElementById("algorithm")

// Definizione palette colori per i ruoli
const ROLE_COLORS = {
    CARRIER:  '#4a2c2a', // Rosso mattone molto scuro/spento
    MOD:      '#ff5722', // Arancione lava (Tipico Elektron)
    CHAIN:    '#ffab00', // Giallo ambra brillante (Focus massimo)
    AMP:      '#FFFFFF'  // Bianco Puro
};


// Mappatura Algoritmi -> Ruoli Operatori (A, B1, B2)
const ALGO_MAPPING = {
    1: { A: 'MOD',    B2: 'MOD',    B1: 'CHAIN' },     
    2: { A: 'MOD',    B2: 'MOD',    B1: 'CARRIER' },
    3: { A: 'MOD',    B2: 'CARRIER',B1: 'CARRIER' },
    4: { A: 'CHAIN',  B2: 'MOD',    B1: 'CHAIN' },
    5: { A: 'CHAIN',  B2: 'MOD',    B1: 'CHAIN' },
    6: { A: 'MOD',    B2: 'MOD',    B1: 'CARRIER' },
    7: { A: 'MOD',    B2: 'MOD',    B1: 'CARRIER' },
    8: { A: 'MOD',    B2: 'CARRIER',B1: 'CARRIER'}
};

// Oggetto per memorizzare le istanze per accesso rapido via suffisso
let adsrRegistry = {};

window.addEventListener('load', () => {
    
    // 1. Inizializza AMP (sempre bianco)
    if(document.getElementById('adsrCanvas_amp')) {
        adsrRegistry['amp'] = new ADSRVisualizer('amp', ROLE_COLORS.AMP);
    }

    // --- LOGICA AGGIUNTA ---
    // Recuperiamo l'algoritmo corrente
    const algorithmKnob = document.getElementById("algorithm");
    const currentAlgo = algorithmKnob ? (parseInt(algorithmKnob.value) || 1) : 1;
    
    // Recuperiamo la mappa dei ruoli per questo algoritmo (es. { A: 'MOD', B1: 'CHAIN'... })
    const currentMap = ALGO_MAPPING[currentAlgo]; 

    // 2. Inizializza Operatori con il colore GIUSTO da subito
    ['A', 'B1', 'B2'].forEach(suffix => {
        if(document.getElementById(`adsrCanvas_${suffix}`)) {
            
            // A. Cerchiamo il ruolo nella mappa. Se non c'è, fallback a CARRIER
            const role = (currentMap && currentMap[suffix]) ? currentMap[suffix] : 'CARRIER';
            
            // B. Otteniamo il colore
            const initialColor = ROLE_COLORS[role];

            // C. Passiamo il colore direttamente al costruttore
            adsrRegistry[suffix] = new ADSRVisualizer(suffix, initialColor);
        }
    });

    // 3. Agganciamo il listener per i cambiamenti futuri
    if (algorithmKnob) {
        algorithmKnob.addEventListener('input', (e) => {
            const val = parseInt(e.target.value) || 1;
            setAdsrAlgorithm(val);
        });
    }
});

window.addEventListener('resize', () => {
    Object.values(adsrRegistry).forEach(instance => instance.resize());
});

/**
 * Funzione Pubblica: Chiama questa quando giri la knob Algorithm
 * @param {number} algoIndex - Indice algoritmo (1-8)
 */
function setAdsrAlgorithm(algoIndex) {
    const map = ALGO_MAPPING[algoIndex];
    if (!map) return;

    // Itera su A, B1, B2 definiti nella mappa
    Object.keys(map).forEach(suffix => {
        const role = map[suffix];     // es. 'CARRIER', 'MOD', 'CHAIN'
        const color = ROLE_COLORS[role]; // Recupera il colore hex
        
        // Se l'istanza esiste, aggiorna il colore
        if (adsrRegistry[suffix]) {
            adsrRegistry[suffix].updateColor(color);
        }
    });
}


algorithmKnob.addEventListener('input', (e) => {
    const val = parseInt(e.target.value) || 1;
    setAdsrAlgorithm(val);
});
