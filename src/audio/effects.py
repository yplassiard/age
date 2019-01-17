# *-* coding: utf8 *-*

timeEffects = []

class Effect(object):
    """Basic audio effect that does nothing."""
    stepValue = 0.01
    sound = None
    name = None

    def __init__(self, sound, stepValue):
        super().__init__()
        self.sound = sound
        self.name = self.sound.name
        if self.sound.channel is None:
            raise RuntimeError("Sound {name} does not have any active channel".format(name=self.name))
    
    def __str__(self):
        return "Effect({name})".format(name=self.name)

    def isCompleted(self):
        raise NotImplementedError

    def getLogName(self):
        return "Effect()"
    
class VolumeEffect(Effect):
    """Implements a fade volume effect, either fade in or fade out."""
    expected = None

    def __init__(self, sound, expected, stepValue=0.005):
        super().__init__(sound, stepValue)
        self.expected = expected
        self.curVolume = self.sound.channel.get_volume()
        self.stepValue = stepValue
        if self.curVolume > self.expected:
            self.stepValue = -self.stepValue
    def isCompleted(self):
        if abs(self.sound.channel.get_volume() - self.expected) < 0.01:
            self.sound.channel.set_volume(self.expected)
            if self.expected == 0.0:
                self.sound.stop()
            return True
        return False
    
    def __str__(self):
        return "VolumeEffect(%s)" % self.name

