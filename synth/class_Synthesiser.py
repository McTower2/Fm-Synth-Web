"""
DISCLAIMER:
If you want to use this directory as standalone code (without web part, only code)
you need to unmake the "module pack". To do so: 

1. delete the file __init__.py
2. delete the dot from all the imports (in each file of this directory) 
    example: "from .class_Adsr import Adsr" -> "from class_Adsr import Adsr"
3. create a main.py file
4. copy/paste the code from the Synthesiser example below (right before the constructor)
5. run and enjoy!
6. bonus: you can change preset for every note, just alternate loadPreset(), noteOn(), render(), repeat.

(hope the code speaks for itself, I really tried my best to give good names to methods)
"""
from .class_SynthesiserSound import SynthesiserSound
from .class_SynthesiserVoice import SynthesiserVoice
from .class_PresetManager import PresetManager
from .class_Sequencer import Sequencer
from typing import List
import numpy as np


class Synthesiser:
    """
    Polyphonic FM synthesiser inspired by the Elektron Digitone's "fm Tone".

    *Public components*
    ------------
    - `sound`      : Edit global parameters of the synth
    - `preset`     : Save, load, and print presets
    - `sequencer`  : Create audio from a sequence

    *Example usage*
    -----------------
    >>> from class_Synthesiser import Synthesiser
    >>> synth = Synthesiser(numVoices = 3)
    >>> 
    >>> # change sound parameters
    >>> synth.sound.setAlgorithm(2)
    >>> synth.sound.setLfoParams(1, "c ratio", 3, 1, 3, 0.0)
    >>> synth.sound.setMix(0.35)
    >>> synth.sound.set_ADSR_Amp(a=1000, d=1200, s=1, r=400, amp=1)
    >>> synth.sound.set_ADSR_A(a=750, d=1000, s=0.3, r=1000, lev=4)
    >>> synth.sound.setRatioB1(0.749)
    >>> synth.sound.setFeedbackC(1.3)
    >>> 
    >>> # manage presets
    >>> #synth.preset.saveToFile("my_patch")
    >>> #synth.preset.loadFromFile("my_patch")
    >>> synth.preset.printPresetNames()
    >>> synth.preset.printCurrentPreset()
    >>> 
    >>> # write a simple sequence
    >>> sig = synth.sequencer.create_sequence(["C4", "E4", None, ("C4","E4","G4")], step_len=0.5)
    >>> 
    >>> # play sound
    >>> from sounddevice import play, wait
    >>> play(sig)
    >>> wait()
    """
    def __init__(self, numVoices:int, sample_rate = 44100):
        self._sr = sample_rate
        self.sound = SynthesiserSound(sample_rate = self._sr)
        self.preset = PresetManager(self.sound)
        self.sequencer = Sequencer()
        self.sequencer._initialize_sequencer(self)
        self._voices:List[SynthesiserVoice] = [SynthesiserVoice(sound=self.sound, sample_rate=self._sr) 
                                               for _ in range(numVoices)]
        try:
            for voice in self._voices:
                voice.initialize_modMatrix()
        except: print("Synthesier -> unable to initialize modMatrix")
    

    def noteOn(self, midiNote, numSamples:int=None):
        """Trova una voce libera o rimpiazza quella più vecchia."""
        free_voice = next((v for v in self._voices if not v.isPlaying()), None)
        if free_voice is None: # noteStealing:
            return             # do nothing
        #free_voice.resetOperatorsPhase()
        frequency = self.midiNoteToFreq(midiNote)
        free_voice.noteOn(frequency, numSamples)
    
    def noteOff(self, midiNote):
        frequency = self.midiNoteToFreq(midiNote)
        for voice in self._voices:
            if voice.frequency == frequency:
                voice.noteOff()

    def allNotesOff(self):
        for voice in self._voices:
            voice.noteOff()

    def getNextSample(self):
        """returns the next sample as sum of every voice"""
        smp = sum(v.getNextSample() for v in self._voices)
        return smp

    def render(self, numSamples: int) -> List[float]:
        """renders and returns audio stream for given numSamples"""
        buffer = [0.0] * numSamples
        for i in range(numSamples):
            buffer[i] = self.getNextSample()
        return buffer
    
    def resetPhases(self):
        """ resets operators phase (used in routes/audio_routes.py) """
        for voice in self._voices:
            voice.resetOperatorsPhase()
    
    def resetLfoPhases(self):
        """ resets lfos phase (used in routes/audio_routes.py) """
        for voice in self._voices:
            voice.resetLfosPhase()
    
    @staticmethod
    def midiNoteToFreq(midiNote:int):
        """A4=midiNote(69)=440 Hz;  C4=midiNote(60)"""
        return 440*pow(2, (midiNote-69)/12)




if __name__=="__main__":
    from sounddevice import play, wait
    from matplotlib import pyplot as plt

    synth = Synthesiser(numVoices=3)

    synth.sound.setMix(0.5)
    synth.sound.setAlgorithm(2)
    synth.sound.set_ADSR_Amp(20, 200, 0.4, 100, 0.4)
    synth.sound.setFeedbackC(1.3)
    synth.sound.set_ADSR_A(100, 100, 1, 300, 5)

    synth.sound.setLfoParams(1, 3, 2, 3, 3, 0.0)
    synth.sound.setLfoParams(2, 0, 3.0, 2.0, 0, 0.0)

    sr = 44100
    numSamples = sr*3
    dur_note = sr*2
    sig = []

    synth.noteOn(57, dur_note)
    synth.noteOn(69, dur_note)
    sig += synth.render(numSamples)

    synth.noteOn(76, dur_note)
    for _ in range(numSamples):
        smp = synth.getNextSample()
        sig.append(smp)

   
    play(sig)
    wait()
    # plt.plot(sig)
    plt.show()
