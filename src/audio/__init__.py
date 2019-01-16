# *-* coding: utf-8 *-*

import logger
import constants
import gameconfig
import eventManager
import pygame
import os

from . import effects
from . import sound


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
        for s in gameConfig.getSoundResources():
            logger.info(self, "Loading {name} ({file})".format(name=s["name"], file=s["file"]))
            try:
                snd = sound.Sound(s["name"], s["file"])
                self.soundMap[s["name"]] = snd
            except Exception as e:
                logger.exception(self, "Failed to load {file}: {exception}".format(file=s["file"], exception=e), e)
        global _instance

        _instance = self

    def loadMusic(self, config):
        name = gameconfig.getValue(config, "name", str)
        file = gameconfig.getValue(config, "file", str)
        loop = gameconfig.getValue(config, "loop", int, {"defaultValue": -1})
        if loop is None:
            loop = -1
        if name is None or file is None:
            raise RuntimeError("Missing name or file property for music")
        if self.musicMap.get(name, None) is not None:
            raise RuntimeError("Music's name {name} already defined".format(name=name))
        try:
            logger.info(self, "Loading music {name} ({file})".format(name=name, file=file))
            snd = sound.Music(name, file, loops=loop, fadeIn=True)
        except Exception as e:
            logger.error(self, "Cannot load music {name} ({file}): {exception}".format(name=name, file=file, exception=e))
            return False
        self.musicMap[name] = snd
        return True
    
    def play(self, name, volume, pan=(1.0, 1.0), fadeIn=False):
        snd = self.soundMap.get(name, None)
        left = volume * pan[0]
        right = volume * pan[1]
        if snd is not None:
            snd.play()
            snd.setVolume(left, right)
        else:
            logger.error(self, "Sound {name} is not loaded.".format(name=name))

    def stop(self, name):
        snd = self.soundMap.get(name, None)
        if snd is not None and snd.isPlaying():
            snd.stop()

    def playMusic(self, name, volume=constants.AUDIO_MUSIC_VOLUME, fadeIn=True):
        music = self.musicMap.get(name, None)
        if music is None:
            logger.error(self, "Music {name} not loaded".format(name=name))
            return False
        music.setVolume(volume)
        music.setFadeIn(fadeIn)
        music.play()

    def stopMusic(self, name):
        music = self.musicMap.get(name, None)
        if music is not None:
            music.stop()
    
    def getLogName(self):
        return "AudioManager"


    # events

    def event_leave_scene(self, event):
        s = event.get("scene", None)
        if s is None:
            return
        nextScene = event.get('nextScene', None)
        if nextScene is None:
            nextSceneMusic = []
        else:
            nextSceneMusic = nextScene.getMusics()
        for music in self.musicMap:
            found = False
            for m in nextSceneMusic:
                if m["name"] == music:
                    found = True
            if not found:
                logger.info(self, "stopping {music}".format(music=music))
                self.musicMap[music].stop(fadeOut=True)
        return
    
    def event_scene_interval_tick(self, event):
        now = event.get("time", 0)
        for effect in effects.timeEffects:
            if isinstance(effect, effects.VolumeEffect):
                # logger.info(self, "Adjusting {name}(volume={volume}, step={step})".format(name=effect.name, volume=effect.curVolume, step=effect.stepValue))
                effect.curVolume += effect.stepValue
                effect.sound.channel.set_volume(effect.curVolume)
                if effect.isCompleted():
                    logger.info(self, "Effect {e} completed".format(e=effect))
                    effects.timeEffects.remove(effect)
                    continue
                effect._lastTick = now
    
                    
        
def initialize(gameConfig):
    if _instance is None:
        try:
            am = AudioManager(gameConfig)
            return True
        except Exception as e:
            logger.exception("audio", "Error initializing audio: {exception}".format(exception=e), e)
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

def stopMusic(name):
    global _instance

    _instance.stopMusic(name)

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
