// every parameter's setter function pass from here and goes to python

// float generic parameters
async function sendParam(paramName, value) {
    console.log(`Updating: ${paramName} -> ${value}`);

    try {
        // function defined in ../routes/api_routes.py
        const response = await fetch('/api/update-param', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            // standard json: { "name": "...", "value": ... }
            body: JSON.stringify({ 
                name: paramName, 
                value: value 
            })
        });

        if (!response.ok) throw new Error(response.statusText);
    } catch (error) {
        console.error("sync error:", error);
    }
}

// lfos parameters
async function sendLfoParam(paramName, value, lfoIndex) {
    console.log(`Updating: ${paramName} -> ${value}. lfo index${lfoIndex}`);
    try {
        const response = await fetch('/api/update-lfo-param', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                name: paramName, 
                value: value,
                lfoIndex: lfoIndex
            })
        });

        if (!response.ok) throw new Error(response.statusText);
    } catch (error) {
        console.error("sync error:", error);
    }
}

// exponential envelope parameters
async function sendEnvParam(paramName, value) {
    console.log(`Updating: ${paramName} -> ${value}.`);
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
        console.error("sync error:", error);
    }
}

// specific for algorithm parameter (int)
async function setAlgorithm(paramName, value) {
    console.log("Updating algorithm:", value);
    try {
        const response = await fetch('/api/set-algorithm', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ algorithm: value })
        });
        if (!response.ok) throw new Error(response.statusText);
    } catch (error) {
        console.error("Error while sending the parameter:", error);
    }

}