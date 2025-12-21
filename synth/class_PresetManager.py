from .class_SynthesiserSound import SynthesiserSound
from dataclasses import asdict

DEFAULT_PRESET_FILE_NAME = "./FmSynth_presets.txt"

class PresetManager:
    def __init__(self, sound:SynthesiserSound):
        self.sound = sound
    
    def saveToFile(self, name: str, filename: str = DEFAULT_PRESET_FILE_NAME):
        """Salva un preset nel file, evitando duplicati di nome."""
        if name == "":
            print('non puoi salvare un preset senza nome "" ')
        if self._checkExistingPresetName(name, filename):
            print(f"Il preset '{name}' esiste già. Inserire un altro nome.")
            return
        line = f"{name}: {self.params_to_dict()}\n"
        with open(filename, "a", encoding="utf-8") as f:
            f.write(line)
        print(f"Preset '{name}' salvato con successo in {filename}.")

    def loadFromFile(self, presetName: str, filename: str = DEFAULT_PRESET_FILE_NAME):
        """
        Carica un preset da file.

        Parametri
        ----------
        presetName : str
            Nome del preset da caricare.
        filename : str, opzionale
            Nome del file (default: DEFAULT_PRESET_FILE_NAME).
        """
        # Controlla che il preset esista nel file
        try:
            f = open(filename, "r", encoding="utf-8")
        except FileNotFoundError:
            print(f"File '{filename}' non trovato (directory corrente non corretta?).")
            raise

        with f:
            found = False
            for line in f:
                line = line.strip()
                if not line or not line.startswith(presetName + ":"):
                    continue

                _, dict_str = line.split(":", 1)
                dict_str = dict_str.strip()
                preset_dict = eval(dict_str)
                self.dict_to_params(preset_dict)
                print(f"Preset '{presetName}' caricato correttamente da {filename}.")
                found = True
                break

        if not found:
            print(f"Preset '{presetName}' non trovato in {filename}.")
            raise FileNotFoundError(f"Preset '{presetName}' non trovato in {filename}.")

    def printPresetNames(self, filename: str = DEFAULT_PRESET_FILE_NAME):
        names = []
        try:
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    names.append(line.split(":")[0])
                print(names)
        except Exception:
            print(f"filename '{filename}' not found")

    def printCurrentPreset(self):
        params:dict = self.params_to_dict()
        for k, v in params.items():
            print(f"{k}: {v}")

    def _fetchSetters(self):
        """Ritorna una lista di metodi 'set' pubblici e validi dell'oggetto."""
        methods = []
        for name in dir(self.sound):
            if name.startswith('set') and not name.startswith("set_"):
                methods.append(name)
        return methods
    
    def _fetchGetters(self):
        """Ritorna una lista di metodi 'get' pubblici e validi dell'oggetto."""
        methods = []
        for name in dir(self.sound):
            if name.startswith('get') and not name.startswith("get_"):
                methods.append(name)
        return methods
    
    def params_to_dict(self) -> dict:
        results = {}

        for method_name in self._fetchGetters():
            method = getattr(self.sound, method_name)
            key = method_name[3:]

            # Caso speciale: LFO multipli
            if method_name == "getLfoParams":
                for key, lfo in self.sound.lfos.items():
                    params = self.sound.getLfoParams(key)
                    # converte in tupla (se dataclass o oggetto normale)
                    if hasattr(params, "__dataclass_fields__"):
                        value = tuple(asdict(params).values())
                    elif hasattr(params, "__dict__"):
                        value = tuple(vars(params).values())
                    else:
                        value = tuple(params)
                    results[f"Lfo{key}Params"] = value
                continue

            try:
                results[key] = method()
            except TypeError:
                results[key] = None

        return results

    def dict_to_params(self, dict_of_values) -> None:
        for method_name in self._fetchSetters():
            method = getattr(self.sound, method_name)
            key = method_name[3:]

            # Caso speciale: LFO multipli
            if method_name == "setLfoParams":
                for i in self.sound.lfos.keys():
                    lfo_key = f"Lfo{i}Params"
                    if lfo_key in dict_of_values:
                        value = dict_of_values[lfo_key]
                        if isinstance(value, (tuple, list)):
                            method(i, *value)
                        else:
                            method(i, *list(value.__dict__.values()))
                continue

            if key in dict_of_values:
                value = dict_of_values[key]
                if isinstance(value, (tuple, list)):
                    method(*value)
                else:
                    method(value)

    # ==============================================================
    #   FILE I/O
    # ==============================================================


    def _checkExistingPresetName(self, presetName: str, filename: str = DEFAULT_PRESET_FILE_NAME) -> bool:
        """Controlla se esiste già un preset con questo nome nel file."""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith(presetName + ":"):
                        return True
        except FileNotFoundError:
            return False
        return False


    
if __name__ == "__main__":
    sound = SynthesiserSound()
    preset = PresetManager(sound)
    #preset.saveToFile("prova")
    #preset.loadFromFile("first_patch")
    print("tutto ok")