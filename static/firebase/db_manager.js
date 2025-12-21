import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getFirestore, collection, addDoc, getDocs, query, where, doc, setDoc 
        } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

import { firebaseConfig } from "./firebase_config.js"; 

// Inizializza Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

// --- FUNZIONI DI SALVATAGGIO E CARICAMENTO ---


// Funzione generica per caricare
export async function loadAllFromFirebase(collectionName) {
    try {
        const querySnapshot = await getDocs(collection(db, collectionName));
        let results = [];
        querySnapshot.forEach((doc) => {
            // Uniamo l'ID del documento ai suoi dati veri e propri
            results.push({ id: doc.id, ...doc.data() });
        });
        return results;
    } catch (e) {
        console.error("Errore caricamento: ", e);
        return [];
    }
}

// Funzione generica per salvare
export async function saveToFirebase(collectionName, dataObj) {
    try {
        const docRef = await addDoc(collection(db, collectionName), {
            ...dataObj,
            timestamp: new Date()
        });
        console.log("Documento salvato con ID: ", docRef.id);
        return true;
    } catch (e) {
        console.error("Errore salvataggio: ", e);
        alert("An error occurred while saving. (Check the console for details)");
        return false;
    }
}

export async function checkIdByName(collectionName, nameToCheck) {
    try {
        const q = query(collection(db, collectionName), where("name", "==", nameToCheck));
        const querySnapshot = await getDocs(q);

        if (!querySnapshot.empty) {
            // Ritorna l'ID del primo risultato trovato
            return querySnapshot.docs[0].id;
        } else {
            return null;
        }
    } catch (e) {
        console.error("Errore check esistenza:", e);
        return null;
    }
}

// Sovrascrive un documento esistente dato il suo ID
export async function overwriteToFirebase(collectionName, docId, dataObj) {
    try {
        const docRef = doc(db, collectionName, docId);
        // setDoc sovrascrive i dati. Usiamo merge: true se volessimo mantenere campi vecchi non specificati,
        // ma per un "Salva Preset" solitamente vogliamo sostituire tutto.
        await setDoc(docRef, {
            ...dataObj,
            timestamp: new Date() // Aggiorniamo la data
        });
        console.log("Documento sovrascritto: ", docId);
        return true;
    } catch (e) {
        console.error("Errore sovrascrittura:", e);
        return false;
    }
}