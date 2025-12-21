from typing import List
from .class_Adsr import Adsr
from .class_SynthesiserSound import SynthesiserSound
from .class_Operator import Operator
from .class_ModMatrix import ModMatrix

class SynthesiserVoice:
    """This class is a child to SynthesiserSound: 
        Every time a noteOn is called, an instance of this class synthesizes the sound, 
        based on the sound parameters defined in SynthesiserSound.
        (This class must not call SynthesiserSound setters, only getters)"""
    def __init__(self, sound:SynthesiserSound, sample_rate:int=44100):
        #fixed variables
        self._sound = sound
        self._sr = sample_rate
        # internal variables used for synthesis
        self._freq:float = 440.0
        self._algo = None
        self._algo_map:dict[int:callable()] = {1: self._algo1, 2: self._algo2, 3: self._algo3, 
                                               4: self._algo4, 5: self._algo5, 6: self._algo6, 
                                               7: self._algo7, 8: self._algo8}
        self._mix_X, self._mix_Y = 0.0, 1.0
        
        self.adsr_amp = Adsr(1, 1, 1, 1, 1, self._sr)
        self.A = Operator(sample_rate = self._sr)
        self.B1 = Operator(sample_rate = self._sr)
        self.B2 = Operator(sample_rate = self._sr)
        self.C = Operator(sample_rate = self._sr)
        self.operators:List[Operator] = [self.A, self.B1, self.B2, self.C]
        self.modMatrix:ModMatrix = None


    def initialize_modMatrix(self):
        """must call this right after the initialization of Voice class to connect the modmatrix to the voice and sound"""
        try:
            self.modMatrix = ModMatrix(sample_rate=self._sr)
            self.modMatrix.initialize_modMatrix(self, self._sound)
        except:
            print("Voice: unable to initialize ModMatrix")

            
    def update_static_parameters(self):
        """sets internal variables equals to the ones stored in _sound state"""
        #generals
        self._algo = self._sound.getAlgorithm()
        self.setMix(self._sound.getMix())
        self._algo_func = self._algo_map.get(self._algo)
        
        a,d,s,r,amp = self._sound.get_ADSR_Amp()
        self.adsr_amp.setParams(a,d,s,r,amp)
        # operators
        for op in self.operators:
            op.setFreq(self._freq)

        self._op_map = zip(
            self.operators,
            [self._sound.get_ADSR_A, self._sound.get_ADSR_B1, self._sound.get_ADSR_B2, None],
            [self._sound.get_Params_A, self._sound.get_Params_B1, self._sound.get_Params_B2, self._sound.get_Params_C]
        )

        for op, adsr_func, param_func in self._op_map:
            if adsr_func: # operators A, B1, B2
                a, d, s, r, lev = adsr_func()
                ratio, fb = param_func()
                op.setAllParameters(ratio, fb, a, d, s, r, lev)
            else: # operator C
                ratio, fb = param_func()
                op.setRatio(ratio)
                op.setFeedback(fb)
        #lfos
        self.modMatrix.update_parameters() # here after voice parameters
        
    def resetOperatorsPhase(self):
        for op in self.operators:
            op.resetPhase()
    
    def resetLfosPhase(self):
        self.modMatrix.resetLfoPhases()

    def isPlaying(self):
        """returns if this voice is free to play a new note"""
        return self.adsr_amp.isPlaying()
    
    @property
    def frequency(self):
        """returns the frequency of the voice"""
        return self._freq

    def setMix(self, value):
        """set mix parameters for channel X, Y"""
        value = min(max(value, 0.0), 1.0)
        self._mix_X = value
        self._mix_Y = 1 - value

    def setAmplitude(self, newAmp):
        """sets amp adsr value. this is a proxy to ADSR clipped between 0 and 1"""
        amp = max(min(newAmp, 1), 0)
        self.adsr_amp.setAmplitude(amp)
    

# SYNTHESIS
    def noteOn(self, frequency:float, numSamples:int=None):
        """updates parameters according to SynthesiserSound and triggers all envelopes. optional: numSamples"""
        self._freq = frequency #first update the internal frequency
        self.update_static_parameters() #then update all parameters
        #trigger all ADSR
        self.adsr_amp.setGate(True, numSamples)
        for op in self.operators:
            op.noteOn(frequency, True, numSamples)
        self.modMatrix.noteOn()
    
    def noteOff(self):
        """sets all the envelopes state to 'release'"""
        self.adsr_amp.setGate(False)
        for op in self.operators: 
            op.noteOff()
    
    def getNextSample(self):
        """returns next sample for this voice"""
        if not self.isPlaying():
            self.modMatrix.advance_lfos() #so they keep running in the back
            return 0.0
        self.modMatrix.apply_modulations() #modulate voice parameters
        # synthesis
        x, y = self._algo_func() #call to algo methods
        smp = y*self._mix_X + x*self._mix_Y #mix X and Y channels
        smp *= self.adsr_amp.getSample() #apply Amp Envelope
        return smp


    def _algo1(self):
        """
        [B2] -> [B1] - ┐ - -> Y 
        [A*] - - - -> [C]  -> x
        """
        b2_mod = self.B2.getNext(0.0) * self.B2.getModulationIndex()
        a_mod  = self.A.getNext(0.0) * self.A.getModulationIndex()

        y = self.B1.getNext(b2_mod) 
        b1_mod = y * self.B1.getModulationIndex()

        x = self.C.getNext(b1_mod + a_mod)

        return (x, y)

    def _algo2(self):
        """
        [B2*] -> [B1] -> Y
        [A] - -> [C]  -> X
        """
        # 1. Modulatori (B2 e A)
        b2_mod = self.B2.getNext(0.0) * self.B2.getModulationIndex()
        a_mod  = self.A.getNext(0.0) * self.A.getModulationIndex()

        y = self.B1.getNext(b2_mod)
        x = self.C.getNext(a_mod)
        return (x, y)

    def _algo3(self):
        """
         ┌> [B2] - - - -> Y
        [A*] -> [B1] ┐ 
         └> [C] -  - + -> x
        """
        a_mod = self.A.getNext(0.0) * self.A.getModulationIndex()

        y = self.B2.getNext(a_mod)
        x = 0.5 * ( self.B1.getNext(a_mod) + self.C.getNext(a_mod) )
        return (x, y)

    def _algo4(self):
        """
                          ┌ - - - - -> Y
        [B2*] -> [B1] -> [A] -> [C] -> X
        """        
        b2_mod = self.B2.getNext(0.0) * self.B2.getModulationIndex()
        b1_mod = self.B1.getNext(b2_mod) * self.B1.getModulationIndex()

        y = self.A.getNext(b1_mod)
        a_mod = y * self.A.getModulationIndex()
        x = self.C.getNext(a_mod)
        return (x, y)
        
    def _algo5(self):
        """
        [B2] - ┐   ┌ - - - - > Y
         ↓     \  | 
        [B1*] -> [A] -> [C] -> X
        """
        b2_mod = self.B2.getNext(0.0) * self.B2.getModulationIndex()
        b1_mod = self.B1.getNext(b2_mod) * self.B1.getModulationIndex()

        y = self.A.getNext(b1_mod + b2_mod)
        a_mod = y * self.A.getModulationIndex()
        x = self.C.getNext(a_mod)
        return (x, y)
        
    def _algo6(self):
        """
        [B2] -> [B1] -> Y
            \  /
            /  \ 
        [A*] -> [C] - > X
        """
        b2_mod = self.B2.getNext(0.0) * self.B2.getModulationIndex()
        a_mod = self.A.getNext(0.0) * self.A.getModulationIndex()        
        total_mod = b2_mod + a_mod

        y = self.B1.getNext(total_mod)
        x = self.C.getNext(total_mod)
        return (x, y)

    def _algo7(self):
        """Algo 7
        ┌ - - - -  ┐   
        B2  - B1 - + - > Y

        ┌ - - - - - ┐ 
        A* -  - C - + -> X
        """
        b2 = self.B2.getNext(0.0) 
        b2_mod = b2 * self.B2.getModulationIndex()
        b1 = self.B1.getNext(b2_mod)
        y = (b1 + b2) * 0.5

        a = self.A.getNext(0.0)
        a_mod = a * self.A.getModulationIndex()
        c = self.C.getNext(a_mod)
        x = (a + c) * 0.5

        return (x, y)

    def _algo8(self):
        """
        B1* - - - - > Y
        
        B2 -  - -┐ 
        A  - C - + -> X
        """
        y = self.B1.getNext(0.0)

        b2 = self.B2.getNext(0.0)
        a_mod = self.A.getNext(0.0) * self.A.getModulationIndex()
        c = self.C.getNext(a_mod)
        x = (c + b2) * 0.5
        return (x, y)


if __name__ == "__main__":
    from sounddevice import play,wait
    s = SynthesiserSound()
    voice = SynthesiserVoice(s)
    voice.initialize_modMatrix()

    sr = 44100
    sig = []
    voice.noteOn(frequency=440.0, numSamples=sr*2) #numSamples = None
    # sovrascrivo la patch di sound
    voice.adsr_amp.setParams(100, 200, 0.2, 500, None) # ampli
    voice.A.setAdsrParams = (2000, 500, 0.5, 500, 6) # a
    voice.B2.setAdsrParams = (0.0, 50, 0.1, 500, 10) # b2
    voice._algo = 5

    for _ in range(sr*4):
        smp = voice.getNextSample()
        sig.append(smp)
        #if i == sr*2:
        #    voice.noteOff()
    play(sig)
    wait()