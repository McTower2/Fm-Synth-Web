from .class_SynthesiserSound import SynthesiserSound
from dataclasses import asdict

DEFAULT_PRESET_FILE_NAME = "./FmSynth_presets.txt"

class PresetManager:
    def __init__(self, sound: SynthesiserSound):
        self.sound = sound
    
    def params_to_dict(self) -> dict:
        """ returns a dictionary with all the values stored in the current synth state """
        results = {}

        for method_name in self._fetchGetters():
            method = getattr(self.sound, method_name)
            key = method_name[3:]

            # Special case: Multiple LFOs
            if method_name == "getLfoParams":
                for key, lfo in self.sound.lfos.items():
                    params = self.sound.getLfoParams(key)
                    # Convert to tuple (if dataclass or standard object)
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
        """ sets the current synth state based on a dictionary of values """
        for method_name in self._fetchSetters():
            method = getattr(self.sound, method_name)
            key = method_name[3:]

            # Special case: Multiple LFOs
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

    def printCurrentPreset(self):
        """ print all the datas present in this preset """
        params: dict = self.params_to_dict()
        for k, v in params.items():
            print(f"{k}: {v}")

    def _fetchSetters(self):
        """Returns a list of public and valid 'set' methods of the object."""
        methods = []
        for name in dir(self.sound):
            if name.startswith('set') and not name.startswith("set_"):
                methods.append(name)
        return methods
    
    def _fetchGetters(self):
        """Returns a list of public and valid 'get' methods of the object."""
        methods = []
        for name in dir(self.sound):
            if name.startswith('get') and not name.startswith("get_"):
                methods.append(name)
        return methods
    
    # ==============================================================
    #   PRESETS FILE I/O
    # ==============================================================
    def saveToFile(self, name: str, filename: str = DEFAULT_PRESET_FILE_NAME) -> None:
        """Saves a preset to the file, preventing duplicate names."""
        if name == "":
            print('Error: Cannot save a preset with an empty name.')
        if self._checkExistingPresetName(name, filename):
            print(f"Preset '{name}' already exists. Please choose another name.")
            return
        line = f"{name}: {self.params_to_dict()}\n"
        with open(filename, "a", encoding="utf-8") as f:
            f.write(line)
        print(f"Preset '{name}' successfully saved to {filename}.")

    def loadFromFile(self, presetName: str, filename: str = DEFAULT_PRESET_FILE_NAME) -> None:
        """
        Loads a preset from a file.

        Parameters
        ----------
        presetName : str
            Name of the preset to load.
        filename : str, optional
            Name of the file (default: ./FmSynth_presets.txt).
        """
        # Check if the preset exists in the file
        try:
            f = open(filename, "r", encoding="utf-8")
        except FileNotFoundError:
            print(f"File '{filename}' not found (incorrect current directory?).")
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
                print(f"Preset '{presetName}' successfully loaded from {filename}.")
                found = True
                break

        if not found:
            print(f"Preset '{presetName}' not found in {filename}.")
            raise FileNotFoundError(f"Preset '{presetName}' not found in {filename}.")

    def printPresetNames(self, filename: str = DEFAULT_PRESET_FILE_NAME) -> None:
        """ Prints a list of the names of existing presets """
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
            print(f"File '{filename}' not found.")

    def _checkExistingPresetName(self, presetName: str, filename: str = DEFAULT_PRESET_FILE_NAME) -> bool:
        """Checks if a preset with this name already exists in the file."""
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
    #preset.saveToFile("test")
    #preset.loadFromFile("first_patch")