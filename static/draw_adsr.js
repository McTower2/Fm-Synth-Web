class ADSRVisualizer {
    constructor(suffix, color = '#00ff88') {
        this.suffix = suffix;
        this.color = color;
        
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

    //converts hexadecimal to rgb
    hexToRgb(hex) {
        hex = hex.replace(/^#/, '');

        // ignore alpha by taking first 6 values
        if (hex.length === 8) {
            hex = hex.substring(0, 6);
        }
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
        const { ctx, inputs, drawW: w, drawH: h, color } = this;

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

        // Draw lines
        ctx.beginPath();
        ctx.moveTo(x0, yBase); // start point
        ctx.lineTo(xA, yPeak); // attack
        ctx.lineTo(xD, ySust); // decay
        ctx.lineTo(xS, ySust); // sustain
        ctx.lineTo(xR, yBase); // release

        ctx.lineJoin = 'round';
        ctx.lineCap = 'round';
        ctx.lineWidth = 3;
        
        // line
        ctx.strokeStyle = color; 
        // line shadow
        ctx.shadowBlur = 15;
        ctx.shadowColor = color;
        
        ctx.stroke();

        ctx.shadowBlur = 0;
        ctx.lineTo(xR, h);
        ctx.lineTo(x0, h);
        ctx.closePath();

        // define gradient
        const rgb = this.hexToRgb(color);
        const grad = ctx.createLinearGradient(0, 0, 0, h);
        
        grad.addColorStop(0, `rgba(${rgb}, 0.4)`); // opacity 0.4
        grad.addColorStop(1, `rgba(${rgb}, 0.0)`); // opacity 0
        
        ctx.fillStyle = grad;
        ctx.fill();

        // dots
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

// COLORS Logic
let algorithmKnob = document.getElementById("algorithm")

const ROLE_COLORS = {
    CARRIER:  '#4a2c2a',
    MOD:      '#ff5722',
    CHAIN:    '#ffab00',
    AMP:      '#FFFFFF' 
};

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

let adsrRegistry = {};

window.addEventListener('load', () => {
    
    // initialize amp
    if(document.getElementById('adsrCanvas_amp')) {
        adsrRegistry['amp'] = new ADSRVisualizer('amp', ROLE_COLORS.AMP);
    }

    const algorithmKnob = document.getElementById("algorithm");
    const currentAlgo = algorithmKnob ? (parseInt(algorithmKnob.value) || 1) : 1;
    const currentMap = ALGO_MAPPING[currentAlgo]; 

    // initialize operators
    ['A', 'B1', 'B2'].forEach(suffix => {
        if(document.getElementById(`adsrCanvas_${suffix}`)) {
            
            // Get operator's role
            const role = (currentMap && currentMap[suffix]) ? currentMap[suffix] : 'CARRIER';
            
            // get color
            const initialColor = ROLE_COLORS[role];

            // initialize with right color
            adsrRegistry[suffix] = new ADSRVisualizer(suffix, initialColor);
        }
    });

    // automatic redraw based on algorithm changes
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
 * @param {number} algoIndex
 */
function setAdsrAlgorithm(algoIndex) {
    const map = ALGO_MAPPING[algoIndex];
    if (!map) return;

    // Iterate on A, B1, B2
    Object.keys(map).forEach(suffix => {
        const role = map[suffix];     // e.g. 'CARRIER', 'MOD', 'CHAIN'
        const color = ROLE_COLORS[role];
        
        if (adsrRegistry[suffix]) {
            adsrRegistry[suffix].updateColor(color);
        }
    });
}


algorithmKnob.addEventListener('input', (e) => {
    const val = parseInt(e.target.value) || 1;
    setAdsrAlgorithm(val);
});
