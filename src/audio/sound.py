# *-* coding: utf8 *-*

import pygame
import constants
import logger
from . import effects
import os

class Sound(object):
    name = None
    snd = None
    channel = None

    def __init__(self, name, file, volume=constants.AUDIO_FX_VOLUME, loop=False, _isMusic=False):
        super().__init__()
        dir = 'sounds'
        if _isMusic:
            dir = 'musics'
        self.name = name
        self.file = file
        self.volume = volume
        self.channel = None
        self.snd = None
        try:
            self.snd = pygame.mixer.Sound(os.path.join("data", dir, self.file))
        except Exception as e:
            logger.exception(self, "Unable to load soune: {e}".format(e=e), e)
            self.snd = None
            return
    def setVolume(self, left, right=None):
        if right is None:
            right = left
        if self.isPlaying():
            self.channel.set_volume(left, right)
        else:
            logger.warning(self, "Unable to set volume on inactive sound {name}".format(name=self.name))

    def play(self):
        if self.isPlaying():
            self.stop()
        if self.snd is None:
            logger.error(self, "Cannot play a not loaded sound.")
            return False
        try:
            self.channel = self.snd.play()
        except Exception as e:
            logger.exception(self, "Error playing {name}: {e}".format(name=self.name, e=e), e)
            return False
        return True
    def stop(self):
        if self.isPlaying():
            self.snd.stop()
            self.channel = None
            return True
        return False
    def isPlaying(self):
        if self.channel is None:
            return False
        return self.channel.get_busy()

    def getLogName(self):
        return "Sound(%s, %s)" %(self.name, self.file)

class Music(Sound):
    loops = -1
    def __init__(self, name, file, volume=constants.AUDIO_FX_VOLUME, fadeIn=True, loops=-1):
        super().__init__(name, file, volume, _isMusic=True)
        self.loops = loops
        self.fadeIn = fadeIn

    def play(self):
        if self.isPlaying():
            self.stop()
        try:
            self.channel = self.snd.play(loops=self.loops)
            if self.fadeIn:
                self.channel.set_volume(0)
                effects.timeEffects.append(effects.VolumeEffect(self, self.volume))
            else:
                self.channel.set_volume(self.volume)
            self.playing = True
        except Exception as e:
            logger.error(self, "Failed to play: {e}".format(e=e))
            return False
        return True
    def stop(self, fadeOut=False):
        if self.isPlaying():
            if fadeOut is False:
                self.snd.stop()
            else:
                effects.timeEffects.append(effects.VolumeEffect(self, 0.0))
            return True
        return False
    
            
        
    def setVolume(self, volume):
        self.volume = volume
    def setFadeIn(self, fadeIn):
        self.fadeIn = fadeIn
    
