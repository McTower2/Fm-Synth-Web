class Envelope_r_exp():
    """ Multiplicative release envelope: exponential decay from 1 to 0. """
    
    def __init__(self, releaseTime:float=0.5, sample_rate:int=44100):
        self._sr = sample_rate

        self._target_floor = 0.0001 
        self._alpha = 0
        self._lastSample = 0
        self._smpIndex:int = 0
        
        self.setRelease(releaseTime)
   
    def _update_Alpha(self):
        # Formula: alpha = (target / start) ^ (1 / steps)
        if self._release_smp > 0:
            self._alpha = self._target_floor ** (1.0 / self._release_smp)
        else:
            self._alpha = 0

    def setRelease(self, release_in_seconds, in_samples:bool = False):
        """ sets release time either in seconds or in samples"""
        if in_samples:
            self._release_smp = max(1, int(release_in_seconds)) # already in samples
        else: 
            self._release_smp = max(1, int(release_in_seconds * self._sr)) # calcolate samples
        self._update_Alpha()
    
    def trig(self):
        """ resets envelope from the start (1.0) """
        self._smpIndex = 0
        self._lastSample = 1.0

    def getSample(self):
        if self._smpIndex >= self._release_smp:
            return 0.0

        value = self._lastSample # get value
        self._lastSample *= self._alpha # update state
        self._smpIndex += 1
        return value

# --- TEST ---
if __name__=="__main__":
    from matplotlib import pyplot as plt
    sr = 44100
    renv = Envelope_r_exp(releaseTime=1.0, sample_rate=sr)

    renv.trig()
    sig = [renv.getSample() for _ in range(sr + 1000)]
    
    
    plt.figure(figsize=(10, 6))
    plt.plot(sig)
    plt.title("Exponential Decay from 1 to 0")
    plt.grid(True)
    plt.show()