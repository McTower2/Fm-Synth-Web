// qui tutte le funzioni setter di parametri che verranno intercettate da python

// funzione per cambiare un generico parametro (solo per parametri float)
async function sendParam(paramName, value) {
    console.log(`Aggiornamento: ${paramName} -> ${value}`);

    try {
        // questa rotta è una funzione definita in ../routes/api_routes.py
        const response = await fetch('/api/update-param', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            // pacchetto standard: { "name": "...", "value": ... }
            body: JSON.stringify({ 
                name: paramName, 
                value: value 
            })
        });

        if (!response.ok) throw new Error(response.statusText);
    } catch (error) {
        console.error("Errore sync:", error);
    }
}

async function sendLfoParam(paramName, value, lfoIndex) {
    console.log(`Aggiornamento: ${paramName} -> ${value}. lfo index${lfoIndex}`);
    try {
        const response = await fetch('/api/update-lfo-param', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            // Inviamo un pacchetto standard: { "name": "...", "value": ... }
            body: JSON.stringify({ 
                name: paramName, 
                value: value,
                lfoIndex: lfoIndex
            })
        });

        if (!response.ok) throw new Error(response.statusText);
    } catch (error) {
        console.error("Errore sync:", error);
    }
}

async function sendEnvParam(paramName, value) {
    console.log(`Aggiornamento: ${paramName} -> ${value}.`);
    try {
        const response = await fetch('/api/update-env-param', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                name: paramName, 
                value: value,
            })
        });

        if (!response.ok) throw new Error(response.statusText);
    } catch (error) {
        console.error("Errore sync:", error);
    }
}

// funzione per modificare un parametro specifico
async function setAlgorithm(paramName, value) {
    console.log("Valore finale (rilascio):", value);
    try {
        const response = await fetch('/api/set-algorithm', { // rotta da chiamare
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ algorithm: value }) // nome del parametro
        });
        if (!response.ok) {throw new Error(`Errore HTTP: ${response.status}`);}
    } catch (error) {
        console.error("Errore nell'invio del dato:", error);
    }

}