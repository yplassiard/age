# *-* coding: utf-8 *-*

import logger
import pygame
import os

_instance = None


class AudioManager(object):
    """Manages all audio resources (sfx, bgm)"""
    soundMap = {}
    musicMap = {}
    

    def __init__(self, gameConfig):
        """Initializes the AudioManager with the help of L{GameConfig} object."""
        if gameConfig is None:
            raise runtime_error("Missing game configuration")
        
        pygame.mixer.init(frequency=44100, channels=2)
        for sound in gameConfig.getSoundResources():
            logger.info(self, "Loading {name} ({file})".format(name=sound["name"], file=sound["file"]))
            try:
                snd = pygame.mixer.Sound(os.path.join("data", "sounds", sound["file"]))
                self.soundMap[sound["name"]] = {"sound": snd, "playing": False, "channel": None}
            except Exception as e:
                logger.error(self, "Failed to load {file}: {exception}".format(file=sound["file"], exception=e))
        global _instance
        _instance = self
    def play(self, name):
        sndInfo = self.soundMap.get(name, None)
        if sndInfo is not None:
            sndInfo["channel"] = sndInfo["sound"].play()
            sndInfo["playing"] = True            
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
    if _instance is not None:
        am = AudioManager(gameConfig)

def play(name):
    global _instance

    _instance.play(name)


