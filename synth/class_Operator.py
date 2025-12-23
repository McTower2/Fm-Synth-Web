from .class_FmFeedbackOsc import FmFeedbackOsc
from .class_Adsr import Adsr
from math import pi

class Operator:
    """ FM Operator class. Composed of an FmFeedbackOsc and an Adsr, it outputs 2 signals:
     -  audio signal of the oscillator (between -1 and 1)
     -  control signal of the Adsr (between 'level' and 0)
     +  note: the Adsr does not affect the amp, it is a Phase Modulation (PM) intensity signal"""
    def __init__(self, frequency=440.0, ratio=1.0, feedback=0.0, 
                 attack=100.0, decay=200.0, sustain=0.4, release=300.0, level=0.0, 
                 sample_rate=44100):
        #constants
        self._sr = sample_rate
        self._sr_smp_to_ms = 1000/self._sr
        self._hz = 2*pi/self._sr
        
        # internal parameters
        self._ratio = ratio
        self._voice_freq = frequency
        self._feedback = feedback

        # Oscillator init
        self.oscillator = FmFeedbackOsc(freq=frequency * ratio, feedback=feedback, sample_rate=self._sr)
        # Adsr init
        self.adsr = Adsr(attack, decay, sustain, release, level)
        self._update_frequency()

    def _update_frequency(self):
        """update internal frequency based on frequency and ratio"""
        self._operator_freq = self._voice_freq * self._ratio # update internal state
        self.oscillator.setFrequency(self._operator_freq) # update oscillator's state

    def getFreq(self):
        """returns the voice frequency (ignoring ratio)"""
        return self._voice_freq

    def setFreq(self, value):
        """set voice frequency (ratio also influences this value)"""
        self._voice_freq = value
        self._update_frequency()

    def getRatio(self):
        """returns operator ratio"""
        return self._ratio

    def setRatio(self, value):
        """sets operator ratio and updates frequency"""
        self._ratio = value
        self._update_frequency()

    def getFeedback(self):
        """returns operator feedback"""
        return self._feedback

    def setFeedback(self, value):
        """sets operator feedback"""
        self._feedback = max(0, value)
        self.oscillator.setFeedback(self._feedback)

    #ADSR
    def _smpToMs(self, value_in_samples):
        """samples to milliseconds converter"""
        return value_in_samples * self._sr_smp_to_ms

    def getAttack(self):
        """returns ADSR attack (time in ms)"""
        return self._smpToMs(self.adsr.getAttack())

    def setAttack(self, value):
        """sets ADSR attack (time in ms)"""
        self.adsr.setAttack(value)

    def getDecay(self):
        """returns ADSR decay (time in ms)"""
        return self._smpToMs(self.adsr.getDecay())

    def setDecay(self, value):
        """sets ADSR decay (time in ms)"""
        self.adsr.setDecay(value)

    def getSustain(self):
        """returns ADSR sustain level"""
        return self.adsr.getSustain()

    def setSustain(self, value):
        """sets ADSR sustain level"""
        self.adsr.setSustain(value)

    def getRelease(self):
        """returns ADSR release time in ms"""
        return self._smpToMs(self.adsr.getRelease())

    def setRelease(self, value):
        """sets ADSR release time in ms"""
        self.adsr.setRelease(value)

    def getLev(self):
        """returns ADSR amplitude (level)"""
        return self.adsr.getAmplitude()

    def setLev(self, value):
        """sets ADSR amplitude (level)"""
        value = max(value, 0)
        self.adsr.setAmplitude(value)


    #group setters
    def setAllParameters(self, ratio, feedback, attack, decay, sustain, release, lev):
        self.setRatio(ratio)
        self._feedback = feedback
        self._attack = attack
        self._decay = decay
        self._sustain = sustain
        self._release = release
        self._lev = lev
        self.adsr.setParams(attack, decay, sustain, release, lev)
        
        self._update_frequency()
        self.oscillator.setFeedback(self._feedback)

    def setAdsrParams(self, params:tuple[float]):
        """set level Adsr parameters. expects: (a, d, s, r, level). each one of them can be None"""
        attack, decay, sustain, release, lev = params
        if attack is not None: self._attack = attack
        if decay is not None: self._decay = decay
        if sustain is not None: self._sustain = sustain
        if release is not None: self._release = release
        if lev is not None: self._lev = lev
        self.adsr.setParams(attack, decay, sustain, release, lev)

    # linkers to subclasses
    def setGate(self, gate: bool, numSamples: int = None):
        """ set the Adsr gate. (optional: for a given number of samples) """
        self.adsr.setGate(gate, numSamples)
    
    def resetPhase(self):
        """resets operator phase to 0"""
        self.oscillator.setPhase(0.0)

    # dsp methods
    def noteOn(self, frequency, gate=True, numSamples=None):
      """updates frequency and start level ADSR (Fm amount)"""
      self.adsr.setGate(gate, numSamples)
      self.freq = frequency

    def noteOff(self):
        """adsr enters release phase"""
        self.adsr.setGate(False)



    def getNext(self, fm_input=0.0):
        """
        Calcola il prossimo campione audio applicando la modulazione in ingresso.
        L'operatore avanza SEMPRE di un passo.
        """
        return self.oscillator.getNextSample(phase_mod_input=fm_input)

    def getModulationIndex(self):
        """
        Restituisce SOLO il valore corrente dell'inviluppo (l'intensità della modulazione).
        Non calcola audio e non avanza fasi.
        """
        return self.adsr.getSample()
    
    



if __name__ == "__main__":
    from sounddevice import play, wait
    A = Operator()
    B1 = Operator()
    B2 = Operator()
    C = Operator()
    
    #in synthvoice
    def algo7():
        """Algo 7
        ┌ - - - -  ┐   
        B2  - B1 - + - > Y

        ┌ - - - - - ┐ 
        A* -  - C - + -> X
        """
        a = A.getNextAudioSample()
        b1 = B1.getNextAudioSample()
        b2 = B2.getNextAudioSample()
        c = C.getNextAudioSample()
        C.fmFrom(A.getFmAmount(False))
        B1.fmFrom(B2.getFmAmount(False))
        x = (a+c)*0.5
        y = (b1 + b2)*0.5
        return (x, y)
    
    def algo5():
        """
        [B2] - ┐   ┌ - - - - > Y
          ↓     \  | 
        [B1*] -> [A] -> [C] -> X
        """
        x = C.getNextAudioSample()
        y = A.getNextAudioSample()
        a_mod = A.getFmAmount(False)
        b2_mod = B2.getFmAmount(True)
        b1_mod = B1.getFmAmount(True)
        C.fmFrom(a_mod)
        B1.fmFrom(b2_mod)
        A.fmFrom(b1_mod + b2_mod)
        return (x, y)

    #testers
    def test1():
        """setters and getters using property"""
        a = Operator()
        print(f"get attack: {a.attack} ms")  # stampa 100.0
        
        a.attack = 150.0  # chiama automaticamente il setter
        print(f"set and get attack: {a.attack} ms")   # stampa 150.0

        a.attack += 50
        print(f"add and get attack: {a.attack} ms")   # stampa 200.0
    
    def test2():
        #Note On
        sr = 44100
        ops = [A, B1, B2, C]
        for op in ops:
            op.setGate(True, sr*1)
        #Sound settings
        mix = 0.5
        A.attack=300
        A.decay=300
        A.sustain=0.1
        A.lev=5

        B2.lev=2
        B2.decay=0.5
        B2.sustain=0

        C.ratio=1
        C.feedback=1.1

        output = []
        for _ in range(sr*2):
            x,y = algo7()
            smp = y*mix + x*(1-mix)
            output.append(smp)
        play(output)
        wait()

    
    
    #test1()
    test2()

