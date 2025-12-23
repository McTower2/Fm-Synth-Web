// draw algorithm diagram dinamically

const totalImages = 8;
const imagePath = '/static/img/algorithms/';
const imageExt = '.png';

let imgElement = null; 
const preloadCache = [];

function initAlgoImages() {
    imgElement = document.getElementById('algoImage');
    
    if (!imgElement) {
        console.warn("WARnING: element <img id='algoImage'> not found inside HTML.");
        return;
    }

    // Preload
    for (let i = 1; i <= totalImages; i++) {
        const img = new Image();
        img.src = `${imagePath}${i}${imageExt}`;
        preloadCache.push(img);
    }
    console.log("Algorithm system initialized correctly.");
}

// When algorithm changes
function updateAlgoImage(val) {
    if (!imgElement) {
        imgElement = document.getElementById('algoImage');
    }
    
    if (!imgElement) return;

    let index = Math.round(parseFloat(val));
    
    if (index < 1) index = 1;
    if (index > totalImages) index = totalImages;

    imgElement.src = `${imagePath}${index}${imageExt}`;
}


window.addEventListener('load', initAlgoImages);