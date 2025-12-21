const playButton = document.getElementById('playButton');
// Creiamo un singolo elemento Audio da riutilizzare
const audio = new Audio();

async function playSound() {
    playButton.disabled = true;
    playButton.textContent = 'Loading';
    playButton.onclick = playSound; 

    let slicedGrid = sequencer_status.slice(0); 

    // PULIZIA E OFFSET
    const OCTAVE_OFFSET = 12; // 1 ottava
    slicedGrid = slicedGrid.map(step => {
        if (!step || step.length === 0) return null;
        return step.map(noteNumber => noteNumber + OCTAVE_OFFSET)
    });
    
    // RIMOZIONE NULL FINALI
    while (slicedGrid.length > 0 && slicedGrid[slicedGrid.length - 1] === null) {
        slicedGrid.pop();
    }

    // payload
    const payload = {
        grid: slicedGrid,       
        step_len: parseFloat(step_len) 
    };

    const jsonString = JSON.stringify(payload);
    const encodedData = encodeURIComponent(jsonString);

    audio.src = `/audio?t=${new Date().getTime()}&data=${encodedData}`;

    try {
        await audio.play();
    } catch (e) {
        console.error("Errore riproduzione:", e);
        resetButtonState(); 
        playButton.textContent = 'Error';
    }
}

// === GESTIONE STOP ===

function stopSound() {
    audio.pause();
    audio.currentTime = 0;
    resetButtonState();
}

// Funzione helper per riportare il bottone allo stato iniziale
function resetButtonState() {
    playButton.disabled = false;
    playButton.textContent = 'Play!';
    playButton.onclick = playSound; // Riassegniamo la funzione di Play
}

// === EVENTI AUDIO ===

// Quando l'audio è effettivamente partito (dopo il caricamento)
audio.onplaying = () => {
    playButton.disabled = false;
    playButton.textContent = 'Stop';
    playButton.onclick = stopSound; 
};

// Quando l'audio finisce naturalmente
audio.onended = () => {
    resetButtonState();
};

// === SHORTCUT TASTIERA ===

document.addEventListener('keydown', function(e) {
    if (e.code === 'Space') {
        
        // Ignora se l'utente scrive in un input
        if (document.activeElement.tagName === 'INPUT') return;

        // Previeni lo scroll
        e.preventDefault();

        // Se il bottone è disabilitato (sta caricando), ignora
        if (playButton.disabled) return;

        if (!e.repeat) {
            // LOGICA TOGGLE:
            // Se l'audio non è in pausa e non è finito -> STOP
            if (!audio.paused && !audio.ended && audio.currentTime > 0) {
                stopSound();
            } else {
                // Altrimenti -> PLAY
                playSound();
            }
        }
    }
});


// LOGICA PER EXPORT WAV
async function exportAudio(btn) {
    if (!confirm("Do you really want to download the WAV file?")) {
        return;
    }

    // DISABILITA IL BOTTONE
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerText = "Processing...";
    btn.style.cursor = "wait";

    try {
        let slicedGrid = sequencer_status.slice(0);
        
        const OCTAVE_OFFSET = 12; 
        slicedGrid = slicedGrid.map(step => {
            if (!step || step.length === 0) return null;
            return step.map(noteNumber => noteNumber + OCTAVE_OFFSET)
        });

        while (slicedGrid.length > 0 && slicedGrid[slicedGrid.length - 1] === null) {
            slicedGrid.pop();
        }

        const payload = {
            grid: slicedGrid,       
            step_len: parseFloat(step_len) 
        };

        const jsonString = JSON.stringify(payload);
        const encodedData = encodeURIComponent(jsonString);

        const downloadUrl = `/audio?t=${new Date().getTime()}&data=${encodedData}&export=true`;

        // aspetta la risposta di flask
        const response = await fetch(downloadUrl);

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const blob = await response.blob();

        // Crea un URL temporaneo per il blob che risiede nella memoria del browser
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'my_sequence.wav'; // Nome del file
        document.body.appendChild(link);
        link.click();
        
        // Pulizia
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

    } catch (error) {
        console.error("Export failed:", error);
        alert("An error occurred during the export of the audio file.");
    } finally {
        // RIABILITA IL BOTTONE
        btn.disabled = false;
        btn.innerText = originalText;
        btn.style.cursor = "default";
    }
}