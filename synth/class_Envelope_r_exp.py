class Envelope_r_exp():
    """ Multiplicative release envelope: exponential decay from 1 to 0. """
    
    def __init__(self, releaseTime:float=0.5, sample_rate:int=44100):
        self._sr = sample_rate
        # Definiamo un valore molto piccolo (epsilon) per calcolare la curva.
        # 0.0001 è circa -80dB, sufficiente per non sentire il "click" quando tronchiamo a 0.
        self._target_floor = 0.0001 
        self._alpha = 0
        self._lastSample = 0
        self._smpIndex:int = 0
        # Inizializza release
        self.setRelease(releaseTime)
   
    def _update_Alpha(self):
        # Formula: alpha = (target / start) ^ (1 / steps)
        # Dato che partiamo da 1, start è omesso. Target è il nostro floor.
        if self._release_smp > 0:
            self._alpha = self._target_floor ** (1.0 / self._release_smp)
        else:
            self._alpha = 0

    def setRelease(self, release_in_seconds, in_samples:bool = False):
        """ sets release time either in seconds or in samples"""
        if in_samples:
            self._release_smp = max(1, int(release_in_seconds))
        else: 
            self._release_smp = max(1, int(release_in_seconds * self._sr))
        self._update_Alpha()
    
    def trig(self):
        """ resets envelope from the start (1.0) """
        self._smpIndex = 0
        self._lastSample = 1.0

    def getSample(self):
        # Se abbiamo superato la durata del release, restituisci 0 assoluto
        if self._smpIndex >= self._release_smp:
            return 0.0
        
        # Output corrente
        value = self._lastSample
        
        # Calcola il prossimo campione
        self._lastSample *= self._alpha
        self._smpIndex += 1
        
        return value

# --- TEST ---
if __name__=="__main__":
    from matplotlib import pyplot as plt
    sr = 44100
    # Impostiamo una release breve per vederla bene nel grafico
    renv = Envelope_r_exp(releaseTime=1.0, sample_rate=sr)

    renv.trig()
    # Generiamo un po' più campioni della release per vedere che va a 0
    sig = [renv.getSample() for _ in range(sr + 1000)]
    
    
    plt.figure(figsize=(10, 6))
    plt.plot(sig)
    plt.title("Exponential Decay from 1 to 0")
    plt.grid(True)
    plt.show()