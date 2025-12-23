import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getFirestore, collection, addDoc, getDocs, query, where, doc, setDoc 
        } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

import { firebaseConfig } from "./firebase_config.js"; 

// initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

// --- LOAD AND SAVE FUNCTIONS ---

export async function loadAllFromFirebase(collectionName) {
    try {
        const querySnapshot = await getDocs(collection(db, collectionName));
        let results = [];
        querySnapshot.forEach((doc) => {
            results.push({ id: doc.id, ...doc.data() });
        });
        return results;
    } catch (e) {
        console.error("ERROR WHILE LOADING FROM DATABASE: ", e);
        return [];
    }
}

export async function saveToFirebase(collectionName, dataObj) {
    try {
        const docRef = await addDoc(collection(db, collectionName), {
            ...dataObj,
            timestamp: new Date()
        });
        console.log("Document with ID: ", docRef.id, " saved");
        return true;
    } catch (e) {
        console.error("ERROR WHILE SAVING TO DATABASE: ", e);
        alert("An error occurred while saving. (Check the console for details)");
        return false;
    }
}

export async function checkIdByName(collectionName, nameToCheck) {
    try {
        const q = query(collection(db, collectionName), where("name", "==", nameToCheck));
        const querySnapshot = await getDocs(q);

        if (!querySnapshot.empty) {
            return querySnapshot.docs[0].id;
        } else {
            return null;
        }
    } catch (e) {
        console.error("Errore check esistenza:", e);
        return null;
    }
}

export async function overwriteToFirebase(collectionName, docId, dataObj) {
    try {
        const docRef = doc(db, collectionName, docId);
        // setDoc overwrites data
        await setDoc(docRef, {
            ...dataObj,
            timestamp: new Date()
        });
        console.log("Document Overwritten: ", docId);
        return true;
    } catch (e) {
        console.error("Overwrite Error:", e);
        return false;
    }
}