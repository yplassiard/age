# *-* coding: utf-8 *-*

import logger
import constants
import gameconfig
import eventManager
import pygame
import os


# Audio subsystem

class Effect(object):
    """Basic audio effect that does nothing."""
    stepValue = 0.01
    sound = None
    channel = None
    name = None

    def __init__(self, sound, stepValue):
        super().__init__()
        self.sound = sound
        self.name = self.sound["name"]
        self.channel = self.sound["channel"]
        if self.channel is None:
            raise RuntimeError("Sound {name} does not have any active channel".format(name=name))
    
    def __str__(self):
        return "Effect({name})".format(name=self.name)

    def isCompleted(self):
        raise NotImplementedError

    def getLogName(self):
        return "Effect()"
    
class VolumeEffect(Effect):
    """Implements a fade volume effect, either fade in or fade out."""
    expected = None

    def __init__(self, sound, expected, stepValue=0.01):
        super().__init__(sound, stepValue)
        self.expected = expected
        self.curVolume = self.channel.get_volume()
        self.stepValue = stepValue
    def isCompleted(self):
        if abs(self.channel.get_volume() - self.expected) < 0.01:
            self.channel.set_volume(self.expected)
            return True
        return False
    
    def __str__(self):
        return "VolumeEffect(%s)" % self.name

    


_instance = None



class AudioManager(object):
    """Manages all audio resources (sfx, bgm)"""
    soundMap = {}
    musicMap = {}
    timeEffects = []
    

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

    def loadMusic(self, config):
        name = gameconfig.getValue(config, "name", str)
        file = gameconfig.getValue(config, "file", str)
        loop = gameconfig.getValue(config, "loop", int)
        if loop is None:
            loop = -1
        if name is None or file is None:
            raise RuntimeError("Missing name or file property for music")
        if self.musicMap.get(name, None) is not None:
            raise RuntimeError("Music's name {name} already defined".format(name=name))
        try:
            logger.info(self, "Loading music {name} ({file})".format(name=name, file=file))
            snd = pygame.mixer.Sound(os.path.join("data", "musics", file))
        except Exception as e:
            logger.error(self, "Cannot load music {name} ({file}): {exception}".format(name=name, file=file, exception=e))
            return False
        self.musicMap[name] = {"music": snd,
                               "name": name,
                               "scene": config.get('scene', None),
                               "channel": None,
                               "loop": loop}
        return True
    
    def play(self, name, volume, pan=(1.0, 1.0), fadeIn=False):
        sndInfo = self.soundMap.get(name, None)
        left = volume * pan[0]
        right = volume * pan[1]
        if sndInfo is not None:
            if sndInfo["channel"] is not None:
                sndInfo["channel"].play(sndInfo["sound"])
            else:
                sndInfo["channel"] = sndInfo["sound"].play()
            if fadeIn is False:
                sndInfo["channel"].set_volume(left, right)
            else:
                sndInfo["channel"].set_volume(0, 0)
                self.timeEffects.append(VolumeEffect(sndInfo, volume))
            sndInfo["playing"] = True
            # logger.debug(self, "Playing {name}({volume}, {left}, {right})".format(name=name, volume=volume, left=left, right=right))
        else:
            logger.error(self, "Sound {name} is not loaded.".format(name=name))

    def stop(self, name):
        sndInfo = self.soundMap.get(name, None)
        if sndInfo is not None and sndInfo["playing"] is True:
            sndInfo["sound"].stop()
            sndInfo["playing"] = False

    def playMusic(self, name, volume=constants.AUDIO_MUSIC_VOLUME, fadeIn=True):
        musicInfo = self.musicMap.get(name, None)
        if musicInfo is None:
            logger.error(self, "Music {name} not loaded".format(name=name))
            return False
        musicInfo["channel"] = musicInfo["music"].play()
        if fadeIn is False:
            musicInfo["channel"].set_volume(volume)
        else:
            musicInfo["channel"].set_volume(0)
            self.timeEffects.append(VolumeEffect(musicInfo, volume))
            
    def getLogName(self):
        return "AudioManager"


    # events

    def event_scene_interval_tick(self, event):
        now = event.get("time", 0)
        for effect in self.timeEffects:
            if isinstance(effect, VolumeEffect):
                logger.info(self, "Adjusting {name}(volume={volume}, step={step})".format(name=effect.name, volume=effect.curVolume, step=effect.stepValue))
                effect.curVolume += effect.stepValue
                effect.channel.set_volume(effect.curVolume)
                if effect.isCompleted():
                    logger.info(self, "Effect {e} completed".format(e=effect))
                    self.timeEffects.remove(effect)
                    continue
                effect._lastTick = now
    
                    
        
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
def playMusic(name, volume=constants.AUDIO_MUSIC_VOLUME, fadeIn=True):
    global _instance

    _instance.playMusic(name, volume)


def loadMusic(config):
    global _instance

    return _instance.loadMusic(config)

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
