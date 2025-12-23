from .class_LFO import LFO
from .class_Envelope_r_exp import Envelope_r_exp
from typing import List


class ModMatrix:
    """ ModMatrix composed of modulation sources and destinations. 
    applies modulations dynamically and in real-time to the synthesiserVoice class """
    def __init__(self, sample_rate = 44100):
        self._sr = sample_rate

        self._sr = sample_rate

        # lists of functions
        self._mod_base_values = []
        self._mod_destinations = []
        
        #lfos
        self.lfos = []
        self._apply_lfo = []
        self._lfoBase = []
        self._lfoAmount = []

        # release envelope
        self.env = Envelope_r_exp(sample_rate=self._sr)
        self._apply_env = None
        self._envBase = None
        self._envAmount = None

        # reference class
        self.sound = None # read from
        self.voice = None # write to
        
    def initialize_modMatrix(self, voice, sound):
        """ you must call this method from the voice to connect the matrix
         -  to the sound (to read static parameters)
         -  and to the voice (to modulate parameters)"""
        from .class_SynthesiserSound import SynthesiserSound
        from .class_SynthesiserVoice import SynthesiserVoice
        assert isinstance(voice, SynthesiserVoice)
        assert isinstance(sound, SynthesiserSound)
        self.voice = voice
        self.sound = sound

        # modulators need a method to call to be able to modulate
        self._mod_destinations = [
            self.voice.setMix,                 # 0
            self.voice.setAmplitude,           # 1
            self.voice.A.setRatio,             # 2
            self.voice.A.setLev,               # 3
            self.voice.A.setFeedback,          # 4
            self.voice.B1.setRatio,            # 5
            self.voice.B1.setLev,              # 6
            self.voice.B1.setFeedback,         # 7
            self.voice.B2.setRatio,            # 8
            self.voice.B2.setLev,              # 9
            self.voice.B2.setFeedback,         # 10
            self.voice.C.setRatio,             # 11
            self.voice.C.setFeedback,          # 12
            ]
        # create an lfo for each defined in SyntesiserSound
        self.lfos = [LFO(sample_rate=self._sr) for _ in sound.lfos]
        self._apply_lfo = [None] * len(self.lfos)
        self._lfoBase = [None] * len(self.lfos)
        self._lfoAmount = [None] * len(self.lfos)

    def update_parameters(self):
        #modulators need to know the "center" value of the modulation
        self._mod_base_values = [
            self.sound.getMix(),
            self.voice.adsr_amp.getAmplitude(),
            self.voice.A.getRatio(),
            self.voice.A.getLev(),
            self.voice.A.getFeedback(),
            self.voice.B1.getRatio(),
            self.voice.B1.getLev(),
            self.voice.B1.getFeedback(),
            self.voice.B2.getRatio(),
            self.voice.B2.getLev(),
            self.voice.B2.getFeedback(),
            self.voice.C.getRatio(),
            self.voice.C.getFeedback(),
        ]

        # update lfos
        for i, lfo_params in self.sound.lfos.items():
            idx = i - 1  # LFO1 → index 0
            dest = lfo_params.dest
            if dest is not None:
                self.lfos[idx].setParams(lfo_params.frequency, lfo_params.waveform, lfo_params.smooth)
                self._apply_lfo[idx] = self._mod_destinations[dest]
                self._lfoBase[idx] = self._mod_base_values[dest]
                self._lfoAmount[idx] = lfo_params.amount
        
        # update envelope (only 1)
        dest = self.sound.envDestination
        if dest is not None:
            self._envBase = self._mod_base_values[dest]
            self._apply_env = self._mod_destinations[dest]
            self._envAmount = self.sound.getEnvAmount()
            self.env.setRelease(self.sound.getEnvRelease())
        

    def noteOn(self):
        self.env.trig() # restart the envelope


    def apply_modulations(self):
        """ Apply modulations according to destinations and parameters 
        newValue = centerValue + (modSource * modAmount)
        note: parameters come from SynthesiserSound """
        # LFO
        for lfo, apply_fn, base, amount in zip(self.lfos, self._apply_lfo, self._lfoBase, self._lfoAmount):
            if apply_fn is not None:
                mod_val = base + lfo.getNextSample() * amount
                apply_fn(mod_val)
        # ENVELOPE
        if self._apply_env is not None:
            mod_val = self._envBase + self.env.getSample() * self._envAmount
            self._apply_env(mod_val)

    def advance_lfos(self):
        """ make lfos advance (use this to keep them running in the back) """
        for lfo in self.lfos:
            _ = lfo.getNextSample()

    def resetLfoPhases(self):
        for lfo in self.lfos:
            lfo.set_phase(0.0)
