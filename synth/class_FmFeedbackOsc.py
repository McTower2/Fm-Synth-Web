from math import pi, sin

class FmFeedbackOsc:
    def __init__(self, freq=440.0, feedback=0.0, phase=0.0, mul=1.0, sample_rate=44100):
        self._frequency = freq
        self._feedback = feedback
        self._sr = sample_rate
        self._phase = phase
        self._mul = mul
        
        # Feedback history
        self._old0 = 0.0
        self._old1 = 0.0
        
        self._twoPi = 2 * pi
        self._hz = self._twoPi / self._sr
        self._freqRad = self._frequency * self._hz

    def setFrequency(self, freq: float):
        self._frequency = freq
        self._freqRad = self._frequency * self._hz

    def setFeedback(self, fb: float):
        self._feedback = fb

    def setPhase(self, phase: float):
        self._phase = phase % self._twoPi

    def getCurrentSample(self, phase_mod_input=0.0):
        """
        Restituisce il campione corrente.
        phase_mod_input: modulazione esterna in radianti (NON persistente)
        """
        # Calcolo Feedback
        fb_in = 0.5 * (self._old0 + self._old1)
        internal_mod = fb_in * self._feedback

        total_phase = self._phase + internal_mod + phase_mod_input
        
        sample = sin(total_phase)
        return sample

    def getNextSample(self, phase_mod_input=0.0):
        """
        Restituisce il campione e avanza la fase.
        """
        sample = self.getCurrentSample(phase_mod_input)
        
        # Update feedback history
        self._old1 = self._old0
        self._old0 = sample
        
        # Avanzamento fase (solo frequenza base, la modulazione non si accumula!)
        self._phase += self._freqRad
        if self._phase >= self._twoPi: 
            self._phase -= self._twoPi
            
        return sample