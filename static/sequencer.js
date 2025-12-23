const MAX_STEPS = 64;       
const MAX_POLYPHONY = 6;    
const VISIBLE_OCTAVES = 3;
const SCROLL_THRESHOLD = 30;
let scrollAccumulator = 0;
const gridContainer = document.getElementById('sequencerGrid');


// MODEL
let baseOctave = parseInt(document.getElementById('octaveInput').value); 
let bpm = parseInt(document.getElementById('bpmInput').value);
let note_type = eval(document.getElementById('noteLengthSelect').value);
let step_len = 60/bpm*note_type;

let sequencer_status = new Array(MAX_STEPS).fill(null);

// CONTROL  
function updateOctave(newVal) {
    const el = document.getElementById('octaveInput');
    baseOctave = Math.max(el.min, Math.min(el.max, parseInt(newVal) || el.min))
    el.value = baseOctave
    render();
}

function updateBpm(newVal) {
    const el = document.getElementById('bpmInput');
    bpm = Math.max(el.min, Math.min(el.max, parseInt(newVal) || el.min))
    el.value = bpm
    step_len = 60/bpm*note_type;
    console.log("Nuovi BPM impostati a:", bpm);
}

function updateNoteLength(newVal){
    note_type = eval(newVal);
    step_len = 60/bpm*note_type;
    console.log("Nuovo note lenght impostato a:", newVal);
}

// VIEW

function render() {
    const container = document.getElementById('sequencerGrid');
    container.innerHTML = ''; 

    // MIDI range
    const startMidi = baseOctave * 12; 
    const endMidi = startMidi + (VISIBLE_OCTAVES * 12) - 1;

    for (let midi = endMidi; midi >= startMidi; midi--) {
        createRow(midi, container);
    }

    createTimeline(container);
}

// numbered measures
function createTimeline(container) {
    const row = document.createElement('div');
    row.className = 'timeline-row';

    // Left space for piano keys
    const spacer = document.createElement('div');
    spacer.className = 'timeline-key-spacer';
    row.appendChild(spacer);

    // Numbered cells
    for (let step = 0; step < MAX_STEPS; step++) {
        const cell = document.createElement('div');
        cell.className = 'timeline-cell';
        
        // Measure number every 4 steps
        if (step % 4 === 0) {
            const measureNumber = (step / 4) + 1;
            cell.innerText = measureNumber;
            cell.classList.add('measure-start');
        }

        row.appendChild(cell);
    }

    container.appendChild(row);
}

// Grid
function createRow(midiNote, container) {
    const row = document.createElement('div');
    row.className = 'seq-row';

    // Piano keys on the left
    const noteIndex = midiNote % 12;
    const isBlackKey = [1, 3, 6, 8, 10].includes(noteIndex);
    
    const keyDiv = document.createElement('div');
    keyDiv.className = 'piano-key ' + (isBlackKey ? 'key-black' : 'key-white');
    
    if (noteIndex === 0) { // write C-Octave
        const oct = Math.floor(midiNote / 12);
        keyDiv.innerText = "C" + oct;
    }
    row.appendChild(keyDiv);

    // Cell Steps
    const bgClass = isBlackKey ? 'row-bg-black' : 'row-bg-white';

    for (let step = 0; step < MAX_STEPS; step++) {
        const cell = document.createElement('div');
        cell.className = `step-cell ${bgClass}`;
        
        // if active note
        const stepData = sequencer_status[step];
        if (stepData && stepData.includes(midiNote)) {
            cell.classList.add('active');
        }
        // define interaction
        cell.onclick = () => toggleNote(step, midiNote);

        row.appendChild(cell);
    }

    container.appendChild(row);
}

// Control
function toggleNote(step, midiNote) {
    // init sequencer status
    if (sequencer_status[step] === null) {
        sequencer_status[step] = [];
    }

    const currentStepNotes = sequencer_status[step];
    const index = currentStepNotes.indexOf(midiNote);

    if (index > -1) {
        // A) remove existing note
        currentStepNotes.splice(index, 1);
        if (currentStepNotes.length === 0) {
            sequencer_status[step] = null;
        }
    } else {
        // B) add new note 
        if (currentStepNotes.length >= MAX_POLYPHONY) {
            console.warn(`Max polyphony reached (${MAX_POLYPHONY} notes) for step ${step+1}`);
            return; 
        }
        currentStepNotes.push(midiNote);
        currentStepNotes.sort((a, b) => a - b);
    }

    render();
}

// EVENT LISTENER SCROLL
gridContainer.addEventListener('wheel', (evt) => {
    // 1. Blocchiamo sempre lo scroll di default della pagina
    evt.preventDefault(); 

    if (evt.shiftKey) {
        // --- CASO A: Tasto SHIFT premuto -> SCROLL ORIZZONTALE ---
        gridContainer.scrollLeft += evt.deltaY * 2.1;
    } else {
        // --- CASO B: Solo rotellina -> CAMBIO OTTAVA ---
        scrollAccumulator += evt.deltaY;

        if (Math.abs(scrollAccumulator) >= SCROLL_THRESHOLD) {
            const direction = Math.sign(scrollAccumulator) * -1;
            baseOctave += direction;
            // Limiti: non andare oltre le ottave supportate (0-8)
            if (baseOctave < 0) baseOctave = 0;
            if (baseOctave > 8) baseOctave = 8; 

            updateOctave(baseOctave);
            
            // Resettiamo l'accumulatore dopo il cambio avvenuto
            scrollAccumulator = 0;
        }
    }
}, { passive: false });



// ================= TRANSPOSE FUNCTION =================
/**
* @param {number} semitones
*/
function transposeAll(semitones) {
    let noteChanged = false; // must redraw or not

    // cycle on the steps
    for (let i = 0; i < sequencer_status.length; i++) {
        let stepNotes = sequencer_status[i];

        // if contains notes
        if (stepNotes && stepNotes.length > 0) {
            sequencer_status[i] = stepNotes.map(note => {
                let newNote = note + semitones;
                const floor = 12;
                const Ceiling = 95;
                if (newNote < floor) newNote = floor;
                if (newNote > Ceiling) newNote = Ceiling;
                
                return newNote;
            });
            noteChanged = true;
        }
    }

    if (noteChanged) {
        render(); // redraw
    }
}

// --- INIT ---
// Default data
sequencer_status[0] = [36]; // C3

render();









// --- FIREBASE ---

// save sequence
window.getSequencerState = function() {
    return {
        sequence: sequencer_status, 
        baseOctave: baseOctave,
        bpm: bpm,
        note_type: document.getElementById('noteLengthSelect').value,
    };
};

// load sequence
window.applySequencerState = function(data) {
    console.log("Applicazione sequenza:", data);

    if (data.sequence){
        sequencer_status = data.sequence
    }
    if (data.baseOctave) {
        setValueAndChange('octaveInput', data.baseOctave); 
    }
    if (data.bpm){
        setValueAndChange('bpmInput', data.bpm)
    }
    if (data.note_type){
        setValueAndChange('noteLengthSelect', data.note_type)
    }
    
};