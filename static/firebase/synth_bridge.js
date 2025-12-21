import { saveToFirebase, loadAllFromFirebase, checkIdByName, overwriteToFirebase } from "./db_manager.js";

// ==========================================
// GESTIONE SYNTH PRESET
// ==========================================
export async function handleSavePreset() {
    try {
        console.log("Richiesta parametri al Synth Python...");

        // Nota: '/api' deriva dal prefix del tuo blueprint in server.py
        const response = await fetch('/api/synth/preset'); 
        if (!response.ok) { throw new Error("Errore nella risposta del server Python"); }

        //  dizionario parametri che arriva da python: params_to_dict()
        const presetData = await response.json(); 
        console.log("Dati ricevuti da Python:", presetData);

        const name = prompt("Preset Name:", "");
        if (!name) return; // Annulla se l'utente preme Cancel

        const existingId = await checkIdByName("presets", name);

        if (existingId) {
            // NOME PRESET ESISTENTE: CONFERMI?
            const userConfirmed = confirm(`Preset '${name}' already exists.\nDo you wish to override it?`);
            
            if (userConfirmed) {
                // SOVRASCRIVI
                await overwriteToFirebase("presets", existingId, {
                    name: name, type: "synth_patch", data: presetData
                });
            } else { // Utente ha cliccato "Annulla" nel confirm
                console.log("Salvataggio annullato dall'utente.");
                return; 
            }
        } else {
            // 3b. CASO NUOVO: SALVA NORMALE
            await saveToFirebase("presets", { 
                name: name, type: "synth_patch", data: presetData 
            });
        }
        } catch (e) {
        console.error("Errore save preset:", e);
        alert("Error while saving preset.");
    }
}


// mappa per tradurre parametri python a ID HTML
const PARAM_MAP = {
    "Algorithm": "algorithm",
    //"Amp": non deve essere gestito qua. è destinazione di modulazione ma non parametro visibile all'utente
    "AttackA": 'attack_A',
    "AttackAmp": 'attack_amp',
    "AttackB1": 'attack_B1',
    "AttackB2": 'attack_B2',
    "DecayA": 'decay_A',
    "DecayAmp": 'decay_amp',
    "DecayB1": 'decay_B1',
    "DecayB2": 'decay_B2',
    "EnvAmount": 'envamt',
    "EnvDestination": 'envdest',
    "EnvRelease": 'envrelease',
    "FeedbackA": 'feedback_A',
    "FeedbackB1": 'feedback_B1',
    "FeedbackB2": 'feedback_B2',
    "FeedbackC": 'feedback_C',
    "LevA": 'level_A',
    "LevB1": 'level_B1',
    "LevB2": 'level_B2',
    "Lfo1Params": 'lfo1',
    "Lfo2Params": 'lfo2',
    "Lfo3Params": 'lfo3',
    "MasterVolume": 'master_vol',
    "Mix": 'mix',
    "RatioA": 'ratio_A',
    "RatioB1": 'ratio_B1',
    "RatioB2": 'ratio_B2',
    "RatioC": 'ratio_C',
    "ReleaseA": 'release_A',
    "ReleaseAmp": 'release_amp',
    "ReleaseB1": 'release_B1',
    "ReleaseB2": 'release_B2',
    "SustainA": 'sustain_A',
    "SustainAmp": 'sustain_amp',
    "SustainB1": 'sustain_B1',
    "SustainB2": 'sustain_B2',
    };


// Funzione interna per applicare i dati al frontend
function applyPresetState(presetData) {
    console.log("Applicazione Preset:", presetData);

    const lfoSuffixes = ["dest", "amt", "rate", "wave", "smooth"];

    for (const [pythonKey, value] of Object.entries(presetData)) {
        
        const htmlId = PARAM_MAP[pythonKey]; // HTML id to change the object value

        if (!htmlId) {
            console.warn(`Chiave Python '${pythonKey}' ignorata (nessun ID HTML mappato).`);
            continue;
        }

        // DIRAMAZIONE: È un Array (LFO) o un valore singolo?
        if (Array.isArray(value)) {
            // CASO LFO (Array di valori) - htmlId qui vale "lfo1", "lfo2" o "lfo3"
            
            value.forEach((val, index) => {
                // Costruiamo l'ID finale: "lfo1" + "rate" = "lfo1rate"
                if (val === null) { val = "None"; } // per LfoDestination
                const suffix = lfoSuffixes[index];
                const targetId = htmlId + suffix; 
                
                // Aggiorniamo il singolo parametro dell'LFO
                if (typeof window.setValueAndChange === 'function') {
                    window.setValueAndChange(targetId, val);
                }
            });

        } else {
            // CASO STANDARD (Valore singolo)
            
            let finalValue = value;
            // Fix per EnvDestination: Python None -> HTML "None"
            if (finalValue === null) { finalValue = "None"; }

            // Aggiorniamo il parametro standard
            if (typeof window.setValueAndChange === 'function') {
                window.setValueAndChange(htmlId, finalValue);
            }
        }
    }
}

export async function handleLoadPreset() {
    try {
        // Scarica da Firebase
        const presets = await loadAllFromFirebase("presets");
        
        if (presets.length === 0) {
            alert("No Preset Found.");
            return;
        }

        // Menu di scelta ->  numero: nome_preset
        let msg = "ID Preset:\n" + presets.map((p, i) => `${i}: ${p.name}`).join("\n");
        const choice = prompt(msg);

        if (choice !== null && presets[choice]) {
            const selectedData = presets[choice].data; // Questo è il dizionario Python

            // APPLICAZIONE TRAMITE FRONTEND
            applyPresetState(selectedData);
        }
    } catch (e) {
        console.error("Errore load preset:", e);
    }
}

// ==============================
// GESTIONE SEQUENZE
// ==============================

// SAVE
export async function handleSaveSequence() {
    try {
        if (typeof window.getSequencerState !== 'function') {
            alert("Error: sequencer.js doesn't have the right function");
            return;
        }
        const rawSeqData = window.getSequencerState();
        const dataString = JSON.stringify(rawSeqData);

        const name = prompt("Sequence Name:", "");
        if (!name) return; // Annulla se l'utente preme Cancel o lascia vuoto

        // 3. Controllo se esiste già una sequenza con questo nome
        const existingId = await checkIdByName("sequences", name);

        if (existingId) {
            //CASO ESISTENTE: Chiedi conferma per sovrascrivere
            const userConfirmed = confirm(`Sequence '${name}' already exists.\nDo you wish to overwrite it?`);
            
            if (userConfirmed) {
                // SOVRASCRIVI
                await overwriteToFirebase("sequences", existingId, {
                    name: name, type: "sequencer_data", content: dataString
                });
                console.log(`Sequence '${name}' overwritten.`);
            } else { 
                // ANNULLA
                console.log("Save cancelled by user.");
                return; 
            }
        } else {
            // 4b. CASO NUOVO: Salva normalmente
            await saveToFirebase("sequences", {
                name: name, type: "sequencer_data", content: dataString
            });
        }

    } catch (error) {
        console.error("Error saving sequence:", error);
        alert("Error while saving sequence.");
    }
}

// LOAD
export async function handleLoadSequence() {
    try {
        // Scarica lista dal DB
        const sequences = await loadAllFromFirebase("sequences");
        
        if (sequences.length === 0) {
            alert("There are no Sequences saved.");
            return;
        }

        // Crea menu di scelta
        let msg = "ID sequence to insert:\n";
        sequences.forEach((seq, index) => {
            msg += `${index}: ${seq.name}\n`;
        });
        
        const choice = prompt(msg);
        
        // Applica se valido
        if (choice !== null && sequences[choice]) {
            const dataString = sequences[choice].content;
            const dataToLoad = JSON.parse(dataString);

            // Chiama la funzione in sequencer.js
            if (typeof window.applySequencerState === 'function') {
                window.applySequencerState(dataToLoad);
                //alert(`Sequenza '${sequences[choice].name}' caricata!`);
            } else {
                console.error("Function applySequencerState not found.");
            }
        }
    } catch (error) {
        console.error("Errore load sequence:", error);
    }
}

// (Opzionale) Esponi queste funzioni globalmente per poterle chiamare dall'HTML
window.handleSaveSequence = handleSaveSequence;
window.handleLoadSequence = handleLoadSequence;