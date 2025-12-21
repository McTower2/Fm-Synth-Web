// Configurazione
const totalImages = 8;
const imagePath = '/static/img/algorithms/';
const imageExt = '.png';

// Variabile globale, ma la riempiamo dopo
let imgElement = null; 
const preloadCache = [];

// Funzione di inizializzazione (chiamata al caricamento pagina)
function initAlgoImages() {
    // 1. Ora cerchiamo l'elemento. Se non c'è, usciamo senza errori.
    imgElement = document.getElementById('algoImage');
    
    if (!imgElement) {
        console.warn("ATTENZIONE: Elemento <img id='algoImage'> non trovato nell'HTML.");
        return;
    }

    // 2. Preload delle immagini
    for (let i = 1; i <= totalImages; i++) {
        const img = new Image();
        img.src = `${imagePath}${i}${imageExt}`;
        preloadCache.push(img);
    }
    console.log("Sistema immagini Algoritmi inizializzato.");
}

// Funzione chiamata dalla manopola
function updateAlgoImage(val) {
    // Se imgElement non è stato ancora trovato (es. pagina non caricata), riproviamo
    if (!imgElement) {
        imgElement = document.getElementById('algoImage');
    }
    
    // Se ancora non esiste (magari hai tolto l'html), fermati qui per evitare il crash
    if (!imgElement) return;

    let index = Math.round(parseFloat(val));
    
    if (index < 1) index = 1;
    if (index > totalImages) index = totalImages;

    imgElement.src = `${imagePath}${index}${imageExt}`;
}

// Avvia tutto solo quando la finestra ha finito di caricare l'HTML
window.addEventListener('load', initAlgoImages);