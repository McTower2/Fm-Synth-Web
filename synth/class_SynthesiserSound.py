from dataclasses import dataclass

@dataclass
class LfoParams:
    dest: int = None
    amount: float = 0.5
    frequency: float = 1.0
    waveform: int = 0
    smooth: float = 0.0


@dataclass
class SynthesiserSound:
    """ Synthesiser official parameters container.
     stores parameters for:
      * operators: (ratio, feedback)
      * Adsr envelopes: (a,d,s,r,level)
      * LFOs: (destination, frequency, waveform, smooth)
      * exponential envelope: (release, amount)
      * ModMatrix: (destination, amount) """
    def __init__(self, masterVolume = 1,
                 algorithm:int=1, mix=0.5, 
                 
                 ratio_A:float=1.0, feedback_A=0.0, lev_A=0.0, 
                 attack_A=100.0, decay_A=200.0, sustain_A=1, release_A=300.0, 
                 
                 ratio_B1:float=1, feedback_B1:float=0, lev_B1:float=0, 
                 attack_B1=100.0, decay_B1=200.0, sustain_B1=1, release_B1=300.0, 
                 
                 ratio_B2:float=1, feedback_B2:float=0, lev_B2:float=0, 
                 attack_B2=100.0, decay_B2=200.0, sustain_B2=1, release_B2=300.0, 
                 
                 ratio_C:float=1.0, feedback_C=0.0, 
                 
                 attack_amp=100.0, decay_amp=300.0, sustain_amp=0.8, release_amp=400.0, 
                 amp=1, sample_rate:int=44100):
        
        # general parameters
        self._masterVolume = masterVolume
        self._algorithm = algorithm
        self._mix = mix
        self._attack_amp = attack_amp
        self._decay_amp = decay_amp
        self._sustain_amp = sustain_amp
        self._release_amp = release_amp
        self._amp = amp
        self._sr = sample_rate
        # operator A
        self._ratio_A = ratio_A
        self._feedback_A = feedback_A
        self._lev_A = lev_A
        self._attack_A = attack_A
        self._decay_A = decay_A
        self._sustain_A = sustain_A
        self._release_A = release_A
        # operator B1
        self._ratio_B1 = ratio_B1
        self._feedback_B1 = feedback_B1
        self._lev_B1 = lev_B1
        self._attack_B1 = attack_B1
        self._decay_B1 = decay_B1
        self._sustain_B1 = sustain_B1
        self._release_B1 = release_B1
        # operator B2
        self._ratio_B2 = ratio_B2
        self._feedback_B2 = feedback_B2
        self._lev_B2 = lev_B2
        self._attack_B2 = attack_B2
        self._decay_B2 = decay_B2
        self._sustain_B2 = sustain_B2
        self._release_B2 = release_B2
        # operator C
        self._ratio_C = ratio_C
        self._feedback_C = feedback_C

        self.lfoDestinationConverter = {
            "mix":0,
            "amp":1,
            "a ratio":2, "a lev":3, "a fb":4,
            "b1 ratio":5, "b1 lev":6, "b1 fb":7,
            "b2 ratio":8, "b2 lev":9, "b2 fb":10,
            "c ratio":11, "c fb": 12
        }
        
        self.lfos = {
            1: LfoParams(),
            2: LfoParams(),
            3: LfoParams(),
        }
        self.envAmount:float = 0.0
        self.envRelease:float = 0.1
        self.envDestination:int = None



# Composite gets
    def get_ADSR_Amp(self):  return (self._attack_amp, self._decay_amp, self._sustain_amp, self._release_amp, self._amp)
    def get_ADSR_A(self):    return (self._attack_A, self._decay_A, self._sustain_A, self._release_A, self._lev_A)
    def get_ADSR_B1(self):   return (self._attack_B1, self._decay_B1, self._sustain_B1, self._release_B1, self._lev_B1)
    def get_ADSR_B2(self):   return (self._attack_B2, self._decay_B2, self._sustain_B2, self._release_B2, self._lev_B2)
    def get_Params_A(self):  return (self._ratio_A, self._feedback_A)
    def get_Params_B1(self): return (self._ratio_B1, self._feedback_B1)
    def get_Params_B2(self): return (self._ratio_B2, self._feedback_B2)
    def get_Params_C(self):  return (self._ratio_C, self._feedback_C)
# Composite sets
    def set_ADSR_Amp(self, a: float = None, d: float = None, s: float = None, r: float = None, amp:float=None):
        if a is not None: self.setAttackAmp(a)
        if d is not None: self.setDecayAmp(d)
        if s is not None: self.setSustainAmp(s)
        if r is not None: self.setReleaseAmp(r)
        if amp is not None: self.setAmp(amp)
    def set_ADSR_A(self, a: float = None, d: float = None, s: float = None, r: float = None, lev:float=None):
        if a is not None: self.setAttackA(a)
        if d is not None: self.setDecayA(d)
        if s is not None: self.setSustainA(s)
        if r is not None: self.setReleaseA(r)
        if lev is not None: self.setLevA(lev)
    def set_ADSR_B1(self, a: float = None, d: float = None, s: float = None, r: float = None, lev:float=None):
        if a is not None: self.setAttackB1(a)
        if d is not None: self.setDecayB1(d)
        if s is not None: self.setSustainB1(s)
        if r is not None: self.setReleaseB1(r)
        if lev is not None: self.setLevB1(lev)
    def set_ADSR_B2(self, a: float = None, d: float = None, s: float = None, r: float = None, lev:float=None):
        if a is not None: self.setAttackB2(a)
        if d is not None: self.setDecayB2(d)
        if s is not None: self.setSustainB2(s)
        if r is not None: self.setReleaseB2(r)
        if lev is not None: self.setLevB2(lev)

# General
    def setMasterVolume(self, value:float): self._masterVolume = max(min(value, 1), 0)

    def getMasterVolume(self): return self._masterVolume

    def getAlgorithm(self): return self._algorithm
    def setAlgorithm(self, algorithm: int):
        """set FM algorithm (1–8)
        ```
        Algo1:
            [B2] -> [B1] - ┐ - -> Y 
            [A*] - - - -> [C]  -> x

        Algo2:
            [B2*] -> [B1] -> Y
            [A] - -> [C]  -> X

        Algo3:
             ┌> [B2] - - - -> Y
            [A*] -> [B1] ┐
             └> [C] -  - + -> X

        Algo4:
                              ┌ - - - - -> Y
            [B2*] -> [B1] -> [A] -> [C] -> X

        Algo5:
            [B2] - ┐  ┌ - - - - > Y
              ↓     \ |
            [B1*] -> [A] -> [C] -> X

        Algo6:
            [B2] -> [B1] -> Y
                \  /
                /  \ 
            [A*] -> [C] - > X

        Algo7:
            ┌ - - - -  ┐
            B2  - B1 - + - > Y
            ┌ - - - - - ┐ 
            A* -  - C - + -> X

        Algo8:
            B1* - - - - > Y
            B2 - - - ┐ 
            A  - C - + -> X
            ```
            """
        if algorithm not in range(1, 9):
            raise ValueError("Algorithm must be in range 1–8")
        self._algorithm = int(algorithm)

    def getMix(self):
        """returns mix parameter (for X ad Y)""" 
        return self._mix
    def setMix(self, mix: float):
        """set operator X-Y mix"""
        self._mix = max(min(mix, 1), 0)

# AMP 
    def getAttackAmp(self): return self._attack_amp
    def setAttackAmp(self, attack): 
        """set amp attack in ms"""
        self._attack_amp = attack
    
    def getDecayAmp(self): return self._decay_amp
    def setDecayAmp(self, decay): 
        """set amp decay in ms"""
        self._decay_amp = decay

    def getSustainAmp(self): return self._sustain_amp
    def setSustainAmp(self, sustain:float): 
        """set amp sustain in range (0...1)"""
        self._sustain_amp = sustain

    def getReleaseAmp(self): return self._release_amp
    def setReleaseAmp(self, release): 
        """set amp release in ms"""
        self._release_amp = release

    def getAmp(self): return self._amp
    def setAmp(self, amp: float):
        """ max Amplitude of the voice """
        self._amp = min(max(0.0, amp), 1)

# Op A
    def getRatioA(self): return self._ratio_A
    def setRatioA(self, ratio: float):
        """set operator A ratio"""
        self._ratio_A = max(0.125, ratio)
    def getFeedbackA(self): return self._feedback_A
    def setFeedbackA(self, fb: float):
        """set operator A feedback amount"""
        self._feedback_A = max(0.0, fb)
    def getLevA(self): return self._lev_A
    def setLevA(self, val: float):
        """set operator A intensity"""
        self._lev_A = max(0.0, val)
    def getAttackA(self): return self._attack_A
    def setAttackA(self, attack):
        """set operator A attack in ms"""
        self._attack_A = attack
    def getDecayA(self): return self._decay_A
    def setDecayA(self, decay):
        """set operator A decay in ms"""
        self._decay_A = decay
    def getSustainA(self): return self._sustain_A
    def setSustainA(self, sustain):
        """set operator A sustain in ms"""
        self._sustain_A = sustain
    def getReleaseA(self): return self._release_A
    def setReleaseA(self, release):
        """set operator A release in ms"""
        self._release_A = release
#B1
    def getRatioB1(self): return self._ratio_B1
    def setRatioB1(self, ratio: float):
        """set operator B1 ratio"""
        self._ratio_B1 = max(0.125, ratio)
    def getFeedbackB1(self): return self._feedback_B1
    def setFeedbackB1(self, fb: float):
        """set operator B1 feedback amount"""
        self._feedback_B1 = max(0.0, fb)
    def getLevB1(self): return self._lev_B1
    def setLevB1(self, val: float):
        """set operator B1 intensity"""
        self._lev_B1 = max(0.0, val)
    def getAttackB1(self): return self._attack_B1
    def setAttackB1(self, attack):
        """set operator B1 attack in ms"""
        self._attack_B1 = attack
    def getDecayB1(self): return self._decay_B1
    def setDecayB1(self, decay):
        """set operator B1 decay in ms"""
        self._decay_B1 = decay
    def getSustainB1(self): return self._sustain_B1
    def setSustainB1(self, sustain):
        """set operator B1 sustain in ms"""
        self._sustain_B1 = sustain
    def getReleaseB1(self): return self._release_B1
    def setReleaseB1(self, release):
        """set operator B1 release in ms"""
        self._release_B1 = release
#B2
    def getRatioB2(self): return self._ratio_B2
    def setRatioB2(self, ratio: float):
        """set operator B2 ratio"""
        self._ratio_B2 = max(0.125, ratio)
    def getFeedbackB2(self): return self._feedback_B2
    def setFeedbackB2(self, fb: float):
        """set operator B2 feedback amount"""
        self._feedback_B2 = max(0.0, fb)
    def getLevB2(self): return self._lev_B2
    def setLevB2(self, val: float):
        """set operator B2 intensity"""
        self._lev_B2 = max(0.0, val)
    def getAttackB2(self): return self._attack_B2
    def setAttackB2(self, attack):
        """set operator B2 attack in ms"""
        self._attack_B2 = attack
    def getDecayB2(self): return self._decay_B2
    def setDecayB2(self, decay):
        """set operator B2 decay in ms"""
        self._decay_B2 = decay
    def getSustainB2(self): return self._sustain_B2
    def setSustainB2(self, sustain):
        """set operator B2 sustain in ms"""
        self._sustain_B2 = sustain
    def getReleaseB2(self): return self._release_B2
    def setReleaseB2(self, release):
        """set operator B2 release in ms"""
        self._release_B2 = release
#C
    def getRatioC(self): return self._ratio_C
    def setRatioC(self, ratio: float):
        """set operator C ratio"""
        self._ratio_C = max(0.125, ratio)
    def getFeedbackC(self): return self._feedback_C
    def setFeedbackC(self, fb: float):
        """set operator C feedback amount"""
        self._feedback_C = max(0.0, fb)

# ModMatrix 
    def setLfoParams(self, index:int, *args):
        """
        **args** (accepted either as tuple or individual arguments)
        >>> index : int, 
        >>> destination : str | int,
        >>> amount : float, 
        >>> frequency : float,
        >>> waveform : int,
        >>> smooth : float\n
        \ndestinations:
        ```
        - "mix", "amp"
        - "a ratio",  "a fb",  "a lev"
        - "b1 ratio", "b1 fb", "b1 lev"
        - "b2 ratio", "b2 fb", "b2 lev"
        - "c ratio",  "c fb"
        ```
        waveforms:
        ```
        - sine: 0
        - triangle: 1
        - saw up: 2
        - saw down: 3
        - square: 4
        ```
        """
        def convert_destination(dest: str) -> int:
            """ converts mod destination from string to integer """
            if isinstance(dest, str):
                if dest not in self.lfoDestinationConverter.keys():
                    raise ValueError(f"SynthesiserSound: destination '{dest}' not valid.")
                return self.lfoDestinationConverter[dest]
            return dest
        
        if index<=0 or index>=4: #check index
            print("SynthesiserSound: lfo index out of range")
            raise ValueError
        if len(args) == 1 and isinstance(args[0], LfoParams): #set from dataClass LfoParams (used for presets logic)
            self.lfos[index] = args[0]
        elif len(args) == 5: #set manually from args
            dest, amount, frequency, waveform, smooth = args
            dest = convert_destination(dest) # string to integer
            self.lfos[index] = LfoParams(dest, amount, frequency, waveform, smooth)
        else:
            print("Invalid LFO parameter format")
            raise ValueError
    
    #LFOS single parameter setters
    def getLfoParams(self, index:int) -> LfoParams:
        """get parameters as a dataclass. you can use it to setLfoParams"""
        return self.lfos[index]


    def setLfoDestination(self, lfoIndex, value):
        """value of type None | int"""
        self.lfos[lfoIndex].dest = value

    def setLfoWaveform(self, lfoIndex, value:int):
        self.lfos[lfoIndex].waveform = value

    def setLfoAmount(self, lfoIndex, value:float):
        self.lfos[lfoIndex].amount = value
        
    def setLfoRate(self, lfoIndex, value:float):
        self.lfos[lfoIndex].frequency = value
        
    def setLfoSmooth(self, lfoIndex, value:float):
        self.lfos[lfoIndex].smooth = value



    def setEnvAmount(self, newAmount:float):
        self.envAmount = newAmount
    def getEnvAmount(self):
        return self.envAmount

    def setEnvRelease(self, release:float):
        """release in seconds"""
        self.envRelease = release
    def getEnvRelease(self):
        return self.envRelease

    def setEnvDestination(self, destination):
        """destination of type None | int"""
        self.envDestination = destination
    def getEnvDestination(self):
        return self.envDestination

    # @staticmethod
    # def printAlgorithms():
    #     print(f"Algo1:\n\t[B2] - - ┐- -> [B1] -> Y\n\t[A*] -> [C] - - - - -> x\n")
    #     print(f"Algo2:\n\t[B2*] -> [B1] -> Y\n\t[A] - -> [C]  -> X\n")
    #     print(f"Algo3:\n\t ┌> [B2] - - - -> Y\n\t[A*] -> [B1] ┐\n\t └> [C] -  - + -> x\n")
    #     print(f"Algo4:\n\t\t\t  ┌ - - - - -> Y\n\t[B2*] -> [B1] -> [A] -> [C] -> X\n")
    #     print(f"Algo5:\n\t[B2] - ┐   ┌ - - - - > Y\n\t  ↓     \  | \n\t[B1*] -> [A] -> [C] -> X\n")
    #     print(f"Algo6:\n\t[B2] -> [B1] -> Y\n\t    \  /\n\t    /  \ \n\t[A*] -> [C] - > X\n")
    #     print(f"Algo7:\n\t┌ - - - -  ┐\n\tB2  - B1 - + - > Y\n\t┌ - - - - - ┐ \n\tA* -  - C - + -> X\n")
    #     print(f"Algo8:\n\tB1* - - - - > Y\n\tB2 -  - -┐ \n\tA  - C - + -> X")

if __name__=="__main__":
    s = SynthesiserSound()
    s.setLfoParams(1, "a fb", 5, 1, 3, 0.0)
    print(s.getLfoParams(1))