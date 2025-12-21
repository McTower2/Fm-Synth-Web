from math import pi, sin

class LFO:
    def __init__(self, frequency=1.0, waveform=0, smoothing=0.0, phase=0.0, sample_rate=44100):
        self.sr = sample_rate
        self.hz = 2*pi/self.sr
        self.twopi = 2*pi
        self.srInv = 1/self.sr
        self._smoothEnabled = False
        self._smoothSamples:int = 0
        self._currentValue = 0.0
        self._targetValue = 0.0
        self._smoothIncrement = 0.0
        # LFO parameters
        self.waveform = waveform
        self.frequency = frequency
        self.phase = phase
        self.setSmoothing(smoothing)

    def _smoothLfo(self, newValue: float) -> float:
        """Interpola verso newValue in _smoothSamples campioni."""
        if not self._smoothEnabled or self._smoothSamples <= 1:
            self._currentValue = newValue
            return newValue

        alpha = 1.0 / self._smoothSamples
        self._currentValue += alpha * (newValue - self._currentValue)
        return self._currentValue

    def setParams(self, freq:float, wave:int, smooth:float):
        self.set_frequency(freq)
        self.setWaveform(wave)
        self.setSmoothing(smooth)

    def setSmoothing(self, smooth: float):
        """
        Imposta lo smoothing dell'LFO in maniera normalizzata tra 0 e 1.
        0 = nessuno smoothing
        1 = massimo smoothing (25% del periodo dell'LFO)
        """
        smooth = min(max(0.0, smooth), 1.0)
        if smooth == 0.0:
            self._smoothEnabled = False
            self._smoothSamples = 0
            return
        self._smoothEnabled = True

        lfo_period_in_samples = 1.0 / (max(self.frequency, 1e-6) * self.srInv)
        max_smooth_samples = lfo_period_in_samples * 0.25
        self._smoothSamples = int(smooth * max_smooth_samples)


    def set_frequency(self, frequency):
        """Imposta la frequenza dell'LFO"""
        self.frequency = frequency

    def set_phase(self, phase):
        """sets lfo phase (normalized between 0 and 1)"""
        self.phase = (phase * self.twopi) % self.twopi

    def setWaveform(self, waveform:int=0):
        """0: sine,  
        1: triangular,  
        2: saw up,  
        3: saw down,  
        4: square"""
        if not waveform in (0, 1, 2, 3, 4):
            raise ValueError("LFO: waveform not valid, must be in range (0, 4)")
        self.waveform = waveform
    
    def getNextSample(self):
        sampleValue = 0.0
        if self.waveform == 0: # Sinusoidale
                sampleValue = sin(self.twopi * self.phase)
        elif self.waveform == 1: #Triangular
            sampleValue = 4.0 * abs(self.phase - 0.5) - 1.0
        elif self.waveform == 2: #Saw UP
            sampleValue = 2.0 * self.phase - 1.0
        elif self.waveform == 3: #Saw down
            sampleValue = -2.0 * self.phase + 1.0
        elif self.waveform == 4: #Square
            sampleValue = (self.phase > 0.5) - (self.phase < 0.5)
        else: 
            print("LFO: waveform index out of range") 
            return
        phaseIncrement = self.frequency * self.srInv
        self.phase += phaseIncrement
        self.phase -= int(self.phase)
        return self._smoothLfo(sampleValue)
    

if __name__== "__main__":
    from matplotlib import pyplot as plt
    def plot(wave, title:str):
        plt.plot(wave)
        plt.xlabel(title)
        plt.show()

    sr = 44100
    l = LFO(1)
    l.setWaveform(4)

    l.setSmoothing(0.0)
    signal = [l.getNextSample() for _ in range(int(sr*4))]
    plot(signal, "Not smoothed")

    l.setSmoothing(0.5)
    signal = [l.getNextSample() for _ in range(int(sr*4))]
    plot(signal, "half smoothed")

    l.setSmoothing(1)
    signal = [l.getNextSample() for _ in range(int(sr*4))]
    plot(signal, "max smoothed")
