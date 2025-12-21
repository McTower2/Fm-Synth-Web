# questo file intercetta le chiamate a fuzione di js (update_parameters.js)
# e reindirizza le richieste al synth python
# la chiamata al setter parte dalla frontend, e tranite questo script raggiunge la backend

from flask import Blueprint, jsonify, current_app, request # <-- Importa current_app e request

api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/synth/preset', methods=['GET'])
def get_synth_preset():
    try:
        synth = current_app.synth
        data_to_send = synth.preset.params_to_dict()
        return jsonify(data_to_send), 200
    except Exception as e:
        print(f"❌ Errore recupero preset: {e}")
        return jsonify({"error": str(e)}), 500


# funzione generica
@api_bp.route('/update-param', methods=['POST'])
def update_param():
    try:
        data = request.get_json()
        param_name = data.get('name')
        value = float(data.get('value'))
        
        synth = current_app.synth

        param_map = {
            'ratio_A': synth.sound.setRatioA,
            'feedback_A': synth.sound.setFeedbackA,
            'level_A': synth.sound.setLevA,
            'attack_A': synth.sound.setAttackA,
            'decay_A': synth.sound.setDecayA,
            'sustain_A': synth.sound.setSustainA,
            'release_A': synth.sound.setReleaseA,
            
            'ratio_B1': synth.sound.setRatioB1,
            'feedback_B1': synth.sound.setFeedbackB1,
            'level_B1': synth.sound.setLevB1,
            'attack_B1': synth.sound.setAttackB1,
            'decay_B1': synth.sound.setDecayB1,
            'sustain_B1': synth.sound.setSustainB1,
            'release_B1': synth.sound.setReleaseB1,
            
            'ratio_B2': synth.sound.setRatioB2,
            'feedback_B2': synth.sound.setFeedbackB2,
            'level_B2': synth.sound.setLevB2,
            'attack_B2': synth.sound.setAttackB2,
            'decay_B2': synth.sound.setDecayB2,
            'sustain_B2': synth.sound.setSustainB2,
            'release_B2': synth.sound.setReleaseB2,
            
            'ratio_C': synth.sound.setRatioC,
            'feedback_C': synth.sound.setFeedbackC,

            'mix' : synth.sound.setMix,

            'attack_amp': synth.sound.setAttackAmp,
            'decay_amp': synth.sound.setDecayAmp,
            'sustain_amp': synth.sound.setSustainAmp,
            'release_amp': synth.sound.setReleaseAmp,
            'master_vol': synth.sound.setMasterVolume,
        }

        # Controllo se il parametro esiste nella mappa
        if param_name in param_map:
            # CHIAMATA DINAMICA: Prende la funzione dal dizionario e la esegue con (value)
            function_to_call = param_map[param_name]
            function_to_call(value)
            
            print(f"[OK] {param_name} impostato a {value}")
            return jsonify({"status": "ok", "param": param_name, "value": value})
        else:
            print(f"[ERR] Parametro sconosciuto: {param_name}")
            return jsonify({"error": f"Parametro '{param_name}' non mappato"}), 400

    except ValueError:
         return jsonify({"error": "Il valore non è un numero valido"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@api_bp.route('/set-algorithm', methods=['POST']) # la stringa deve essere uguale in js
def setAlgorithm():
    try:
        synth = current_app.synth # collegati al synth condiviso
        data = request.get_json() # prendi dati da js
        if not data or 'algorithm' not in data: # la stringa deve essere uguale a js
            return jsonify({"error": "Dati mancanti: chiave 'algorithm' richiesta"}), 400
        new_algorithm = int(data.get('algorithm')) # assicurati di convertire il valore
        synth.sound.setAlgorithm(new_algorithm) 
        return jsonify({
            "status": "success", 
            "message": f"algorithm impostato a {new_algorithm}"
        })
    except ValueError:
        return jsonify({"error": "Il valore inviato non è un numero valido"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/update-lfo-param', methods=['POST'])
def update_lfo_param():
    try:
        data = request.get_json()
        param_name = data.get('name')

        value = None if data.get('value')=="None" else float(data.get('value'))

        #value = float(data.get('value')) # Conversione in float
        if param_name in ['dest', 'wave']: # conversione eccezionale in int
            value = None if value is None else int(value)

        index = int(data.get('lfoIndex'))
        
        synth = current_app.synth
        
        param_map = {
            'dest': synth.sound.setLfoDestination,
            'wave': synth.sound.setLfoWaveform,
            'amount': synth.sound.setLfoAmount,
            'rate': synth.sound.setLfoRate,
            'smooth': synth.sound.setLfoSmooth,
        }

        # Controllo se il parametro esiste nella mappa
        if param_name in param_map:
            # CHIAMATA DINAMICA: Prende la funzione dal dizionario e la esegue con (value)
            function_to_call = param_map[param_name]
            function_to_call(index, value) #setLfoRate(index=1, rate=value)
            
            print(f"[OK] {param_name} impostato a {value}")
            return jsonify({"status": "ok", "param": param_name, "value": value})
        else:
            print(f"[ERR] Parametro sconosciuto: {param_name}")
            return jsonify({"error": f"Parametro '{param_name}' non mappato"}), 400

    except ValueError:
         return jsonify({"error": "Il valore non è un numero valido"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@api_bp.route('/update-env-param', methods=['POST'])
def update_env_param():
    try:
        data = request.get_json()
        param_name = data.get('name')
        value = None if data.get('value')=="None" else float(data.get('value'))
        if param_name == 'dest': # conversione eccezionale in int
            value = None if value is None else int(value)
        
        synth = current_app.synth

        param_map = {
            'dest': synth.sound.setEnvDestination,
            'amount': synth.sound.setEnvAmount,
            'release': synth.sound.setEnvRelease,
        }

        # Controllo se il parametro esiste nella mappa
        if param_name in param_map:
            # CHIAMATA DINAMICA: Prende la funzione dal dizionario e la esegue con (value)
            function_to_call = param_map[param_name]
            function_to_call(value)
            
            print(f"[OK] {param_name} impostato a {value}")
            return jsonify({"status": "ok", "param": param_name, "value": value})
        else:
            print(f"[ERR] Parametro sconosciuto: {param_name}")
            return jsonify({"error": f"Parametro '{param_name}' non mappato"}), 400

    except ValueError:
         return jsonify({"error": "Il valore non è un numero valido"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500