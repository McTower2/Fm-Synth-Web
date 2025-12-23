const RELEASE_KNOB_ID = 'envrelease';
const CANVAS_ID = 'envelopeCanvas';

function drawReleaseEnvelope() {
    const knob = document.getElementById(RELEASE_KNOB_ID);
    const canvas = document.getElementById(CANVAS_ID);

    if (!knob || !canvas) {
        console.warn("Canvas or Knob not found. Check IDs.");
        return;
    }

    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;

    ctx.clearRect(0, 0, w, h);

    // style
    const neonColor = '#d900ff'; 
    ctx.strokeStyle = neonColor;
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.shadowBlur = 15;
    ctx.shadowColor = neonColor;

    // Padding
    const padTop = 5;
    const padBot = 5;

    // normalize value between 0 (min) and 1 (max)
    let min = parseFloat(knob.getAttribute('min')) || 0;
    let max = parseFloat(knob.getAttribute('max')) || 100;
    let current = parseFloat(knob.value);
    if (isNaN(current)) current = min;
    
    let range = max - min;
    if (range <= 0) range = 1; // avoid division by 0
    
    let norm = (current - min) / range;
    if (norm < 0) norm = 0;
    if (norm > 1) norm = 1;
    // decay factor
    // Norm 0 (Min) -> Fast Decay -> High factor (e.g. 15)
    // Norm 1 (Max) -> Slow Decay  -> Low factor (e.g. 0.2)
    const decayFactor = 0.5 + (15 * Math.pow((1 - norm), 2)); 

    // Draw
    ctx.beginPath();
    //attack
    ctx.moveTo(2, h - padBot); 
    ctx.lineTo(2, padTop);
    //release
    for (let x = 2; x <= w; x++) {
        // Normalized x
        let xProgress = (x - 2) / (w - 2); 

        // y = e^(-k * x)
        let amplitude = Math.exp(-decayFactor * xProgress * 3);

        let drawHeight = h - padTop - padBot;
        let y = padTop + ((1 - amplitude) * drawHeight);

        ctx.lineTo(x, y);
    }

    ctx.stroke();
}

// activation on page load
window.addEventListener('load', () => {
    const knob = document.getElementById(RELEASE_KNOB_ID);
    if (knob) {
        drawReleaseEnvelope();
        knob.addEventListener('input', drawReleaseEnvelope);
    }
});