const playButton = document.getElementById('playButton');
const DOWNLOAD_FILE_NAME = 'my_sequence.wav'
const audio = new Audio();

async function playSound() {
    playButton.disabled = true;
    playButton.textContent = 'Loading';
    playButton.onclick = playSound; 

    let slicedGrid = sequencer_status.slice(0); 

    // CLEANING AND OFFSET
    const OCTAVE_OFFSET = 12; // 1 Octave
    slicedGrid = slicedGrid.map(step => {
        if (!step || step.length === 0) return null;
        return step.map(noteNumber => noteNumber + OCTAVE_OFFSET)
    });
    
    // Remove null from the end of the sequence
    while (slicedGrid.length > 0 && slicedGrid[slicedGrid.length - 1] === null) {
        slicedGrid.pop();
    }

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
        console.error("Playback Error:", e);
        resetButtonState(); 
        playButton.textContent = 'Error';
    }
}

// STOP SOUND
function stopSound() {
    audio.pause();
    audio.currentTime = 0;
    resetButtonState();
}

// reset play button
function resetButtonState() {
    playButton.disabled = false;
    playButton.textContent = 'Play!';
    playButton.onclick = playSound;
}

// AUDIO EVENTS 
audio.onplaying = () => {
    playButton.disabled = false;
    playButton.textContent = 'Stop';
    playButton.onclick = stopSound; 
};

audio.onended = () => {
    resetButtonState();
};

// KEYBOARD SHORTCUT
document.addEventListener('keydown', function(e) {
    if (e.code === 'Space') {
        
        // If user is writing, ignore
        if (document.activeElement.tagName === 'INPUT') return;

        // prevent default scroll
        e.preventDefault();

        // ignore if audio is loading
        if (playButton.disabled) return;

        if (!e.repeat) {
            // TOGGLE:
            if (!audio.paused && !audio.ended && audio.currentTime > 0) {
                stopSound();
            } else {
                playSound();
            }
        }
    }
});


// EXPORT WAV
async function exportAudio(btn) {
    if (!confirm("Do you really wish to download the WAV file?")) {
        return;
    }

    // DISABLE BUTTON
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

        // wait for flask response
        const response = await fetch(downloadUrl);

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const blob = await response.blob();

        // create temporary space for the binary file
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = DOWNLOAD_FILE_NAME;
        document.body.appendChild(link);
        link.click();
        
        // Clean
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

    } catch (error) {
        console.error("Export failed:", error);
        alert("An error occurred during the export of the audio file.");
    } finally {
        // REACTIVATE BUTTON
        btn.disabled = false;
        btn.innerText = originalText;
        btn.style.cursor = "default";
    }
}