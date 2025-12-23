from math import pi, sin

class LFO:
    """Simple LFO class with control over frequency, waveform, smoothing, phase"""
    def __init__(self, frequency=1.0, waveform=0, smoothing=0.0, phase=0.0, sample_rate=44100):
        # rates and constants
        self.sr = sample_rate
        self.twopi = 2*pi
        self.hz = self.twopi/self.sr
        self.srInv = 1/self.sr

        #Smoothing parameters
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
        """Interpolates towards newValue in _smoothSamples time."""
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
        Set LFO smoothing value normalized between 0 and 1.
        0 = no smoothing
        1 = max smoothing (25% of LFO period)
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
        """set LFO frequency"""
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
            raise ValueError("LFO: invalid waveform index")
        self.waveform = waveform
    
    def getNextSample(self):
        sampleValue = 0.0
        if self.waveform == 0: # Sinusoid
                sampleValue = sin(self.twopi * self.phase)
        elif self.waveform == 1: #Triangle
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
