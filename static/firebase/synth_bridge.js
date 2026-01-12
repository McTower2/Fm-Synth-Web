import { saveToFirebase, loadAllFromFirebase, checkIdByName, overwriteToFirebase } from "./db_manager.js";

// ==========================================
// SYNTH PRESET
// ==========================================

// save synth preset to database
export async function handleSavePreset() {
    try {
        console.log("Parameters requested to Python Server...");

        const response = await fetch('/api/synth/preset'); 
        if (!response.ok) { throw new Error("Error in Python answer"); }

        const presetData = await response.json(); 
        console.log("Preset data recieved:", presetData);

        const name = prompt("Preset Name:", "");
        if (!name) return; // cancel

        const existingId = await checkIdByName("presets", name);

        if (existingId) { // OVERWRITE FILE
            const userConfirmed = confirm(`Preset '${name}' already exists.\nDo you wish to override it?`);
            
            if (userConfirmed) {
                // overwrite confirmed
                await overwriteToFirebase("presets", existingId, {
                    name: name, type: "synth_patch", data: presetData
                });
            } else { // overwrite canceled
                console.log("Preset save canceled from the user.");
                return; 
            }
        } else {
            // NORMAL SAVE
            await saveToFirebase("presets", { 
                name: name, type: "synth_patch", data: presetData 
            });
        }
        } catch (e) {
        console.error("Error while saving preset:", e);
        alert("Error while saving preset.");
    }
}


// Parameters map. Python:html_ID
const PARAM_MAP = {
    "Algorithm": "algorithm",
    //"Amp": not visible to user
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


// apply preset data to frontend (and backend consequently)
function applyPresetState(presetData) {
    console.log("setting Preset Data:", presetData);

    const lfoSuffixes = ["dest", "amt", "rate", "wave", "smooth"];

    for (const [pythonKey, value] of Object.entries(presetData)) {
        
        const htmlId = PARAM_MAP[pythonKey]; // HTML id to change the object value

        if (!htmlId) { continue; }

        // 2 cases: here it's an LFO (array)
        if (Array.isArray(value)) {
            value.forEach((val, index) => {
                let valToSend = val; 
                if (valToSend === null) { valToSend = "None"; } // LfoDestination safe conversion
                
                const suffix = lfoSuffixes[index];
                const targetId = htmlId + suffix; // e.g. lfo1dest, lfo2amt...
                
                // Update single parameter
                if (typeof window.setValueAndChange === 'function') {
                    window.setValueAndChange(targetId, valToSend);
                }
            });

        } else { // standard case (1 parameter)
            let valueToSend = value;
            if (valueToSend === null) { valueToSend = "None"; } // envDestination safe conversion

            // Update single parameter
            if (typeof window.setValueAndChange === 'function') {
                window.setValueAndChange(htmlId, valueToSend);
            }
        }
    }
}

// Load synth preset from database
export async function handleLoadPreset() {
    try {
        // Download from Firebase
        const presets = await loadAllFromFirebase("presets");
        
        if (presets.length === 0) {
            alert("No Preset Found.");
            return;
        }

        // existing presets list ->  Number: preset_name
        let msg = "ID Preset:\n" + presets.map((p, i) => `${i}: ${p.name}`).join("\n");
        const choice = prompt(msg);

        if (choice !== null && presets[choice]) {
            const selectedData = presets[choice].data; //preset values dictionary

            applyPresetState(selectedData);
        }
    } catch (e) {
        console.error("Error while loading preset:", e);
    }
}

// ==============================
// SEQUENCES
// ==============================

// SAVE
export async function handleSaveSequence() {
    try {
        if (typeof window.getSequencerState !== 'function') {
            alert("Error: saving function not found");
            return;
        }
        const rawSeqData = window.getSequencerState();
        const dataString = JSON.stringify(rawSeqData);

        const name = prompt("Sequence Name:", "");
        if (!name) return; // Cancel

        // does the name already exist?
        const existingId = await checkIdByName("sequences", name);

        if (existingId) { // case overwrite
            const userConfirmed = confirm(`The name '${name}' already exists.\nDo you wish to overwrite the sequence?`);
            
            if (userConfirmed) {
                // overwrite
                await overwriteToFirebase("sequences", existingId, {
                    name: name, type: "sequencer_data", content: dataString
                });
                console.log(`Sequence '${name}' overwritten.`);
            } else { 
                // cancel overwrite
                console.log("Save cancelled by user.");
                return; 
            }
        } else {
            // normal save
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
        // download from DB
        const sequences = await loadAllFromFirebase("sequences");
        
        if (sequences.length === 0) {
            alert("There are no Sequences saved.");
            return;
        }

        // Presets menu
        let msg = "ID sequence to insert:\n";
        sequences.forEach((seq, index) => {
            msg += `${index}: ${seq.name}\n`;
        });
        
        const choice = prompt(msg);
        
        // apply if valid
        if (choice !== null && sequences[choice]) {
            const dataString = sequences[choice].content;
            const dataToLoad = JSON.parse(dataString);

            // Call function in sequencer.js
            if (typeof window.applySequencerState === 'function') {
                window.applySequencerState(dataToLoad);
            } else {
                console.error("Function applySequencerState not found.");
            }
        }
    } catch (error) {
        console.error("Error while loading sequence preset:", error);
    }
}

window.handleSaveSequence = handleSaveSequence;
window.handleLoadSequence = handleLoadSequence;