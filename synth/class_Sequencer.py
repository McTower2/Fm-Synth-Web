import numpy as np

class Sequencer:
    def __init__(self):
        self.synth = None
        self.note_map = {
            "C": 0, "C#": 1, "DB": 1,
            "D": 2, "D#": 3, "EB": 3,
            "E": 4,
            "F": 5, "F#": 6, "GB": 6,
            "G": 7, "G#": 8, "AB": 8,
            "A": 9, "A#": 10, "BB": 10,
            "B": 11
        }

    # ---------------------------
    # PUBLIC INTERFACE
    # ---------------------------
    def create_sequence(self, sequence: list, step_len: float, numLoops: int = 1, sample_rate=44100) -> np.ndarray[float]:
        """
        Simple polyphonic sequencer with fixed step length.

        Each element of 'sequence' can be:
            - None      → silence
            - int       → MIDI note number
            - str       → note name (e.g. 'C4', 'F#3')
            - tuple of int and/or str → multiple notes at once
        
        Step_len expressed in seconds\n
        Example
        ```
        mySequence = [('c4', 'e4'), 'f4', 'a4', None,
                  ('g4', 'd4'), 'e4', ('c4', 'g3'), 'c3']
        audio_output = synth.sequencer.create_sequence(mySequence, step_len = 0.5)
        ```
        """
        step_samples = int(step_len * sample_rate)
        sig : np.ndarray[float] = np.zeros(0)

        for _ in range(numLoops):
            for step in sequence:
                notes_to_play = self._parse_step(step)
                self._trigger_notes(notes_to_play, step_samples)
                sig = np.concatenate((sig, self.synth.render(step_samples)))
        sig = np.concatenate((sig, self._render_release_tail(sample_rate)))

        # NORMALIZATION
        peak = np.max(np.abs(sig))
        if peak > 0:
            sig = sig / peak * self.synth.sound.getMasterVolume()
        return sig

    # ---------------------------
    # INTERNAL HELPERS
    # ---------------------------
    def _initialize_sequencer(self, synth):
        """attach synthesiser to this class"""
        self.synth = synth

    def _parse_step(self, step):
        """Converte uno step della sequenza in una lista di note MIDI."""
        if step is None:
            # Silence step
            return []

        if isinstance(step, int):
            return [step]

        if isinstance(step, str):
            return [self.note_str_to_midi(step)]

        if isinstance(step, tuple):
            return [self._convert_note(n) for n in step]

        raise TypeError(f"Tipo di step non valido: {type(step)}")

    def _convert_note(self, note):
        """Converte una singola nota (str o int) in MIDI number."""
        if isinstance(note, int):
            return note
        if isinstance(note, str):
            return self.note_str_to_midi(note)
        raise TypeError(f"Tipo di nota non valido: {type(note)}")

    def _trigger_notes(self, notes: list, step_samples: int):
        """Invoca noteOn per ciascuna nota dello step."""
        for note in notes:
            self.synth.noteOn(note, step_samples)

    def _render_release_tail(self, sample_rate):
        """Renderizza la coda del suono (release)."""
        tail_len = int(self.synth.sound.getReleaseAmp() * 0.001 * sample_rate)
        return self.synth.render(tail_len)

    # ---------------------------
    # NOTE NAME → MIDI CONVERSION
    # ---------------------------

    def note_str_to_midi(self, note_str: str) -> int:
        """
        Converte una nota (es. 'C4', 'C#3', 'Bb2') nel numero MIDI corrispondente.
        C4 = 60 (nota centrale del pianoforte).
        """
        note_str = note_str.strip().upper()
        # Divide nota e ottava
        i = 0
        while i < len(note_str) and not (note_str[i].isdigit() or note_str[i] == "-"):
            i += 1
        note_name = note_str[:i]
        octave_str = note_str[i:]
        if note_name not in self.note_map:
            raise ValueError(f"Nota non riconosciuta: '{note_name}'")
        try:
            octave = int(octave_str)
        except ValueError:
            raise ValueError(f"Ottava non valida in '{note_str}'")
        semitone = self.note_map[note_name]
        midi_number = 12 * (octave + 1) + semitone
        if not (0 <= midi_number <= 127):
            raise ValueError(f"Nota fuori dal range MIDI: {midi_number}")
        return midi_number

if __name__ == "__main__":
    from sounddevice import play, wait
    from .class_Synthesiser import Synthesiser

    syn=Synthesiser(4)
    seq=Sequencer()
    seq._initialize_sequencer(syn)

    sig = seq.create_sequence(["a4", "c4", None], 0.5, 1)

    play(sig)
    wait()