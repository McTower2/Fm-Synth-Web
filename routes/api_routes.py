# this file connects parameters setting from javaScript (frontend) to Python (backend)

from flask import Blueprint, jsonify, current_app, request

api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/synth/preset', methods=['GET'])
def get_synth_preset():
    try:
        synth = current_app.synth # connect to the synth (Python)
        data_to_send = synth.preset.params_to_dict() # call a method
        return jsonify(data_to_send), 200
    except Exception as e:
        print(f"❌ get_synth_preset Error: {e}")
        return jsonify({"error": str(e)}), 500

# generic dispatcher
@api_bp.route('/update-param', methods=['POST'])
def update_param():
    try:
        data = request.get_json()
        param_name = data.get('name')
        value = float(data.get('value'))
        
        synth = current_app.synth

        param_map = { # map IDs to functions
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

        if param_name in param_map:
            # DYNAMIC CALL
            function_to_call = param_map[param_name]
            function_to_call(value)
            
            print(f"[OK] {param_name} set to {value}")
            return jsonify({"status": "ok", "param": param_name, "value": value})
        else:
            print(f"[ERR] Unknown parameter: {param_name}")
            return jsonify({"error": f"Parameter '{param_name}' not mapped"}), 400

    except ValueError:
         return jsonify({"error": "Invalid parameter value"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@api_bp.route('/set-algorithm', methods=['POST'])
def setAlgorithm():
    try:
        synth = current_app.synth
        data = request.get_json()
        if not data or 'algorithm' not in data:
            return jsonify({"error": "Missing data: key 'algorithm' expected"}), 400
        new_algorithm = int(data.get('algorithm'))
        synth.sound.setAlgorithm(new_algorithm) 
        return jsonify({
            "status": "success", 
            "message": f"algorithm set to {new_algorithm}"
        })
    except ValueError:
        return jsonify({"error": "The value is an invalid number"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/update-lfo-param', methods=['POST'])
def update_lfo_param():
    try:
        data = request.get_json()
        param_name = data.get('name')

        value = None if data.get('value')=="None" else float(data.get('value')) # safe conversion

        if param_name in ['dest', 'wave']: # further conversion
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

        if param_name in param_map:
            function_to_call = param_map[param_name]
            function_to_call(index, value) # e.g. setLfoRate(index=1, rate=value)
            
            print(f"[OK] {param_name} set to {value}")
            return jsonify({"status": "ok", "param": param_name, "value": value})
        else:
            print(f"[ERR] Unknown parameter: {param_name}")
            return jsonify({"error": f"Parameter '{param_name}' not mapped"}), 400

    except ValueError:
         return jsonify({"error": "The value is an invalid number"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@api_bp.route('/update-env-param', methods=['POST'])
def update_env_param():
    try:
        data = request.get_json()
        param_name = data.get('name')
        value = None if data.get('value')=="None" else float(data.get('value')) #safe conversion
        if param_name == 'dest': # forther conversion
            value = None if value is None else int(value)
        
        synth = current_app.synth

        param_map = {
            'dest': synth.sound.setEnvDestination,
            'amount': synth.sound.setEnvAmount,
            'release': synth.sound.setEnvRelease,
        }

        if param_name in param_map:
            function_to_call = param_map[param_name]
            function_to_call(value)
            
            print(f"[OK] {param_name} impostato a {value}")
            return jsonify({"status": "ok", "param": param_name, "value": value})
        else:
            print(f"[ERR] Unknown parameter: {param_name}")
            return jsonify({"error": f"Parameter '{param_name}' not mapped"}), 400

    except ValueError:
         return jsonify({"error": "The value is an invalid number"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500