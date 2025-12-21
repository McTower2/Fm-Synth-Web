# genera l'audio da mandare a javascript
from flask import Blueprint, send_file, current_app, request
import io
import wave
import numpy as np
import json

audio_bp = Blueprint('audio_bp', __name__)

SAMPLERATE = 44100

@audio_bp.route('/audio')
def generate_audio():
    data_str = request.args.get('data')
    # Controlliamo se è un export (trasformiamo la stringa 'true' in booleano)
    is_export = request.args.get('export') == 'true' 
    
    if data_str:
        try:
            # RICEZIONE E PULIZIA DATI GREZZI
            frontend_data = json.loads(data_str)
            
            raw_grid = frontend_data.get('grid', []) 
            step_len = float(frontend_data.get('step_len', 0.5)) 
            
            # 2. TRASFORMAZIONE: Liste -> Tuple
            processed_grid = []
            
            for step in raw_grid:
                if step is None:
                    processed_grid.append(None)
                else:
                    processed_grid.append(tuple(step))
            
            # DEBUG PRINT
            print(f"Grid elaborata: {processed_grid}")
            print(f"Step Length: {step_len}")
            # print(f"Export Mode: {is_export}") # Debug per vedere se l'export è attivo

            # GENERAZIONE E INVIO AUDIO
            try:
                synth = current_app.synth
            except AttributeError:
                print("ERRORE: Impossibile trovare 'app.synth'.")
                return "Errore server", 500
            
            # inizializza la fase degli operatori e degli lfo
            synth.resetPhases()
            synth.resetLfoPhases()

            # Generazione segnale
            sig = synth.sequencer.create_sequence(processed_grid, step_len)
            
            # --- Conversione in WAV ---
            memory_file = io.BytesIO()
            
            # Gestione mono/stereo
            if sig.ndim == 1: n_channels = 1
            elif sig.ndim == 2: n_channels = sig.shape[1]
            else: n_channels = 1 
            
            sig = np.nan_to_num(sig, nan=0.0, posinf=1.0, neginf=-1.0)
            sig = np.clip(sig, -1.0, 1.0)
            pcm_data = (sig * 32767).astype(np.int16)

            with wave.open(memory_file, 'wb') as wf:
                wf.setnchannels(n_channels)
                wf.setsampwidth(2)
                wf.setframerate(SAMPLERATE)
                wf.writeframes(pcm_data.tobytes())
            
            memory_file.seek(0)

            # --- MODIFICA QUI: GESTIONE EXPORT VS PLAY ---
            if is_export:
                # Se è un export, forza il download del file
                return send_file(
                    memory_file, 
                    mimetype='audio/wav',
                    as_attachment=True,             # Dice al browser di scaricare
                    download_name='Fm_sequence.wav'    # Nome del file scaricato
                )
            else:
                # Se è play normale, stream per il player
                return send_file(
                    memory_file, 
                    mimetype='audio/wav'
                )
            
        except json.JSONDecodeError:
            print("Errore JSON")
            return "Errore dati", 400
        except Exception as e:
            print(f"Errore generico: {e}")
            return "Errore server", 500
            
    return "Nessun dato ricevuto", 400