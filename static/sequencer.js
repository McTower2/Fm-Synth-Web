const MAX_STEPS = 64;       
const MAX_POLYPHONY = 6;    
const VISIBLE_OCTAVES = 3;

let baseOctave = parseInt(document.getElementById('octaveInput').value); 
let bpm = parseInt(document.getElementById('bpmInput').value);
let note_type = eval(document.getElementById('noteLengthSelect').value);
let step_len = 60/bpm*note_type;

let sequencer_status = new Array(MAX_STEPS).fill(null);

// ================= FUNZIONI DI CONTROLLO =================
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

// ================= RENDERING CORE =================

function render() {
    const container = document.getElementById('sequencerGrid');
    container.innerHTML = ''; 

    // Calcoliamo il range MIDI
    const startMidi = baseOctave * 12; 
    const endMidi = startMidi + (VISIBLE_OCTAVES * 12) - 1;

    for (let midi = endMidi; midi >= startMidi; midi--) {
        createRow(midi, container);
    }

    createTimeline(container);
}

function createTimeline(container) {
    const row = document.createElement('div');
    row.className = 'timeline-row';

    // Spaziatore sinistro (sotto la colonna dei tasti piano)
    const spacer = document.createElement('div');
    spacer.className = 'timeline-key-spacer';
    row.appendChild(spacer);

    // Celle numerate
    for (let step = 0; step < MAX_STEPS; step++) {
        const cell = document.createElement('div');
        cell.className = 'timeline-cell';
        
        // Ogni 4 step (0, 4, 8...) mettiamo il numero della battuta
        if (step % 4 === 0) {
            // Calcolo matematico: step 0 -> Battuta 1, step 4 -> Battuta 2
            const measureNumber = (step / 4) + 1;
            cell.innerText = measureNumber;
            cell.classList.add('measure-start');
        }

        row.appendChild(cell);
    }

    container.appendChild(row);
}

function createRow(midiNote, container) {
    const row = document.createElement('div');
    row.className = 'seq-row';

    // Tasto Piano (Colonna SX)
    const noteIndex = midiNote % 12;
    const isBlackKey = [1, 3, 6, 8, 10].includes(noteIndex);
    
    const keyDiv = document.createElement('div');
    keyDiv.className = 'piano-key ' + (isBlackKey ? 'key-black' : 'key-white');
    
    if (noteIndex === 0) { // Scrivi C3, C4 ecc. solo sui DO
        const oct = Math.floor(midiNote / 12);
        keyDiv.innerText = "C" + oct;
    }
    row.appendChild(keyDiv);

    // Celle Steps (Colonne DX)
    const bgClass = isBlackKey ? 'row-bg-black' : 'row-bg-white';

    for (let step = 0; step < MAX_STEPS; step++) {
        const cell = document.createElement('div');
        cell.className = `step-cell ${bgClass}`;
        
        // Controllo se la nota è attiva
        const stepData = sequencer_status[step];
        if (stepData && stepData.includes(midiNote)) {
            cell.classList.add('active');
        }
        // Aggiungiamo interazione
        cell.onclick = () => toggleNote(step, midiNote);

        row.appendChild(cell);
    }

    container.appendChild(row);
}

// ================= LOGICA NOTE =================

function toggleNote(step, midiNote) {
    // Inizializza array se era null
    if (sequencer_status[step] === null) {
        sequencer_status[step] = [];
    }

    const currentStepNotes = sequencer_status[step];
    const index = currentStepNotes.indexOf(midiNote);

    if (index > -1) {
        // A) RIMUOVI NOTA ESISTENTE
        currentStepNotes.splice(index, 1);
        if (currentStepNotes.length === 0) {
            sequencer_status[step] = null;
        }
    } else {
        // B) AGGIUNGI NUOVA NOTA (Con limite Max Polyphony)
        if (currentStepNotes.length >= MAX_POLYPHONY) {
            console.warn(`Max polyphony reached (${MAX_POLYPHONY} notes) for step ${step+1}`);
            return; 
        }
        currentStepNotes.push(midiNote);
        currentStepNotes.sort((a, b) => a - b);
    }

    render();
}

// ================= EVENT LISTENER SCROLL =================
const gridContainer = document.getElementById('sequencerGrid');

let scrollAccumulator = 0;
const SCROLL_THRESHOLD = 30; // sensibilità dello scroll verticale sulle ottave

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
 * Sposta tutte le note della sequenza di n semitoni.
 * @param {number} semitones - Esempio: 1 (su), -1 (giù), 12 (ottava su)
 */
function transposeAll(semitones) {
    let noteChanged = false; // Per sapere se dobbiamo ridisegnare

    // Cicla attraverso tutti gli step (da 0 a 63)
    for (let i = 0; i < sequencer_status.length; i++) {
        let stepNotes = sequencer_status[i];

        // Se lo step contiene note
        if (stepNotes && stepNotes.length > 0) {
            // Mappa le note correnti ai nuovi valori
            // Es: [36, 40] + 1 diventa [37, 41]
            sequencer_status[i] = stepNotes.map(note => {
                let newNote = note + semitones;
                if (newNote < 12) newNote = 12;
                if (newNote > 95) newNote = 95;
                
                return newNote;
            });
            noteChanged = true;
        }
    }

    if (noteChanged) {
        render(); // Ridisegna la griglia con le nuove posizioni
    }
}

// --- INIT ---
// Dati di default
sequencer_status[0] = [36]; // C3

render();









// --- AGGIUNTE PER FIREBASE ---

window.getSequencerState = function() {
    return {
        // L'array delle note
        sequence: sequencer_status, 
        
        // Variabili singole
        baseOctave: baseOctave,
        bpm: bpm,
        note_type: document.getElementById('noteLengthSelect').value,
    };
};

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