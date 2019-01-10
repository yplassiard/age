# *-* coding: utf-8 *-*

import logger
import constants
import eventManager
import pygame
import os


# Audio subsystem




_instance = None



class AudioManager(object):
    """Manages all audio resources (sfx, bgm)"""
    soundMap = {}
    musicMap = {}
    

    def __init__(self, gameConfig):
        """Initializes the AudioManager with the help of L{GameConfig} object."""
        if gameConfig is None:
            raise RuntimeError("Missing game configuration")
        eventManager.addListener(self)

        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()
        for sound in gameConfig.getSoundResources():
            logger.info(self, "Loading {name} ({file})".format(name=sound["name"], file=sound["file"]))
            try:
                snd = pygame.mixer.Sound(os.path.join("data", "sounds", sound["file"]))
                self.soundMap[sound["name"]] = {"sound": snd, "playing": False, "channel": None}
            except Exception as e:
                logger.error(self, "Failed to load {file}: {exception}".format(file=sound["file"], exception=e))
        global _instance

        _instance = self

    def play(self, name, volume, pan=(1.0, 1.0)):
        sndInfo = self.soundMap.get(name, None)
        left = volume * pan[0]
        right = volume * pan[1]
        if sndInfo is not None:
            if sndInfo["channel"] is not None:
                sndInfo["channel"].play(sndInfo["sound"])
            else:
                sndInfo["channel"] = sndInfo["sound"].play()
            sndInfo["channel"].set_volume(left, right)
            sndInfo["playing"] = True
            # logger.debug(self, "Playing {name}({volume}, {left}, {right})".format(name=name, volume=volume, left=left, right=right))
        else:
            logger.error(self, "Sound {name} is not loaded.".format(name=name))
    def stop(self, name):
        sndInfo = self.soundMap.get(name, None)
        if sndInfo is not None and sndInfo["playing"] is True:
            sndInfo["sound"].stop()
            sndInfo["playing"] = False
            
    def getLogName(self):
        return "AudioManager"
    
def initialize(gameConfig):
    if _instance is None:
        try:
            am = AudioManager(gameConfig)
            return True
        except Exception as e:
            logger.error("audio", "Error initializing audio: {exception}".format(exception=e))
            return False

def play(name, volume=constants.AUDIO_FX_VOLUME, pan=(1.0, 1.0)):
    global _instance

    _instance.play(name, volume, pan)



def computePan(minValue, maxValue, currentValue):
    step = maxValue - minValue
    x = (currentValue - minValue) / step
    
    l = 1.0
    r = 1.0
    if x < 0.5:
        r -= (1 - x * 2)
        if r < 0.1:
            r = 0.1
    elif x > 0.5:
        l -= 1 - (1 - x) * 2
        if l < 0.1:
            l = 0.1
    return l,r
