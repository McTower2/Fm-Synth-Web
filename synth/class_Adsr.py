class Adsr:
    """
    Linear ADSR envelope defined between 0 and amplitude.
    for the ADSR to start it is necessary to call setGate(True).
    While the gate is on, setGate(False) starts the release phase.
    parameters in milliseconds.
    """

    def __init__(self, attack=10.0, decay=100.0, sustain=0.7, release=200.0, amplitude=1.0, sample_rate=44100):
        self._sr = sample_rate
        self._sr_ms_smp = int(self._sr*0.001) #to get from ms to samples
        self._sr_smp_ms = self._sr*1000 #to get from samples to ms
        
        # times (in samples)
        self._attack = 0
        self._decay = 0
        self._release = 0
        self._sustain = sustain
        self._amplitude = amplitude

        # Envelope state
        self._gate = False
        self._phase = "idle"
        self._value = 0.0
        self._index = 0
        self._gate_countdown = None
        self.setParams(attack, decay, sustain, release)

    def _msecToSmp(self, ms: float) -> int:
        """Converts value from milliseconds to samples"""
        return int(self._sr_ms_smp * ms) #sr*0.001 *milliseconds

    def setParams(self, a=None, d=None, s=None, r=None, amplitude=None, in_samples: bool = False):
        """Set envelope parameters: attack, decay, sustain, release (in milliseconds)"""
        if a is not None: self.setAttack(a, in_samples)
        if d is not None: self.setDecay(d, in_samples)
        if s is not None: self.setSustain(s)
        if r is not None: self.setRelease(r, in_samples)
        if amplitude is not None: self.setAmplitude(amplitude)
    
    def getParams(self):
        """values are stored in samples but returned in milliseconds.
        returns a tuple (a, d, s, r, amplitude)"""
        params = (self._attack*self._sr_smp_ms, self._decay*self._sr_smp_ms, 
                  self._sustain, self._release*self._sr_smp_ms, self._amplitude)
        return params

    def setAttack(self, attack: float, in_samples: bool = False):
        """Set attack parameter in ms or samples"""
        self._attack = max(attack,1) if in_samples else max(self._msecToSmp(attack), 1)
    def getAttack(self):
        """returns attack parameter in samples"""
        return self._attack
    
    def setDecay(self, decay: float, in_samples: bool = False):
        """Set decay parameter in ms or samples"""
        self._decay = max(decay,1) if in_samples else max(self._msecToSmp(decay), 1)
    def getDecay(self):
        """returns decay parameter in samples"""
        return self._decay
    
    def setSustain(self, sustain: float):
        """Set sustain parameter"""
        self._sustain = max(sustain, 0)
    def getSustain(self):
        """returns sustain parameter"""
        return self._sustain
    
    def setRelease(self, release: float, in_samples: bool = False):
        """Set release parameter in ms or samples"""
        self._release = max(release,1) if in_samples else max(self._msecToSmp(release), 1)
    def getRelease(self):
        """returns release parameter in samples"""
        return self._release
    
    def setAmplitude(self, amplitude):
        self._amplitude = amplitude #Note: can be negative
        
    def getAmplitude(self):
        """returns max amplitude of the ADSR"""
        return self._amplitude

    def setGate(self, gate: bool, numSamples: int = None):
        """ Sets the gate (ON=True, OFF=False). 
        if numSamples is specified, the gate will be turned off automatically and release will start.
        Otherwise it must be done manually """
        if gate and not self._gate: # start
            self._gate = True
            self._phase = "attack"
            self._index = 0
            self._gate_countdown = None if numSamples is None else numSamples
        elif not gate and self._gate: # release
            self._gate = False
            self._phase = "release"
            self._index = 0
            self._gate_countdown = None

    def isPlaying(self):
        return self._phase != "idle"

    def getSample(self):
        """ Returns next ADSR sample (remember to setGate before) """
        if not self.isPlaying():
            return 0.0

        if self._gate_countdown is not None:
            self._gate_countdown -= 1
            if self._gate_countdown <= 0:
                self.setGate(False)
                self._gate_countdown = None
        # Attack
        if self._phase == "attack":
            self._value = (self._index / max(1, self._attack))
            self._index += 1
            if self._index >= self._attack:
                self._phase = "decay"
                self._index = 0
        # Decay
        elif self._phase == "decay":
            self._value = 1 + (self._sustain - 1) * (self._index / max(1, self._decay))
            self._index += 1
            if self._index >= self._decay:
                self._phase = "sustain"
                self._index = 0
        # Sustain
        elif self._phase == "sustain":
            self._value = self._sustain
            if not self._gate:
                self._phase = "release"
                self._index = 0
        # Release
        elif self._phase == "release":
            start_val = self._value if self._index == 0 else self._release_start
            self._value = start_val * (1 - self._index / max(1, self._release))
            if self._index == 0:
                self._release_start = start_val
            self._index += 1
            if self._index >= self._release:
                self._phase = "idle"
                self._value = 0.0
                self._index = 0

        return self._value * self._amplitude
    
