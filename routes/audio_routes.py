# generate audio and send to js
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
    # check if it's an export request
    is_export = request.args.get('export') == 'true' 
    
    if data_str:
        try:
            # clean data
            frontend_data = json.loads(data_str)
            raw_grid = frontend_data.get('grid', []) 
            step_len = float(frontend_data.get('step_len', 0.5)) 
            
            # conversion. List -> Tuple
            processed_grid = []
            
            for step in raw_grid:
                if step is None:
                    processed_grid.append(None)
                else:
                    processed_grid.append(tuple(step))
            
            # DEBUG PRINT
            print(f"processed grid: {processed_grid}")
            print(f"Step Length: {step_len}")

            # SOUND GENERATION
            try:
                synth = current_app.synth
            except AttributeError:
                print("ERRORE: Unable to connect to app.synth.")
                return "Errore server", 500
            
            # reset phase at the beginning for coherence
            synth.resetPhases()
            synth.resetLfoPhases()

            # Sound generation
            sig = synth.sequencer.create_sequence(processed_grid, step_len)
            
            # wav conversion
            memory_file = io.BytesIO()
            
            # mono/stereo
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

            # EXPORT VS PLAY
            if is_export:
                return send_file(
                    memory_file, 
                    mimetype='audio/wav',
                    as_attachment=True,
                    download_name='Fm_sequence.wav'
                )
            else: # play
                return send_file(
                    memory_file, 
                    mimetype='audio/wav'
                )
            
        except json.JSONDecodeError:
            print("Errore JSON")
            return "Data Error", 400
        except Exception as e:
            print(f"Generic Error: {e}")
            return "Server Errore", 500
            
    return "No Data Recieved", 400