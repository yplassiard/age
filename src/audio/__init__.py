# *-* coding: utf-8 *-*

import logger
import constants
import core
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
    fmod = None

    
    def __init__(self):
        """Initializes the AudioManager with the help of L{GameConfig} object."""
        eventManager.addListener(self)
        try:
            from . import pyfmodex
            self.fmod = pyfmodex.System()
            self.fmod.init()
            self.listener = self.fmod.listener()
            self.listener.position = [0.0, 0.0, 0.0]
        except Exception as e:
            logger.exception(self, "Failed to load FMOD library: {e}".format(e=e), e)
            raise
        
        for s in gameconfig.getSoundResources():
            logger.info(self, "Loading {name} ({file})".format(name=s["name"], file=s["file"]))
            try:
                snd = sound.Sound(self.fmod, s["name"], s["file"])
                self.soundMap[s["name"]] = snd
            except Exception as e:
                logger.exception(self, "Failed to load {file}: {exception}".format(file=s["file"], exception=e), e)
        global _instance

        _instance = self

    def loadMusic(self, config):
        name = gameconfig.getValue(config, "name", str)
        file = gameconfig.getValue(config, "file", str)
        loop = gameconfig.getValue(config, "loops", int, {"defaultValue": -1})
        volume = gameconfig.getValue(config, "volume", float, {"minValue": 0.0,
                                                               "maxValue": 1.0,
                                                               "defaultValue": constants.AUDIO_MUSIC_VOLUME})
        
        if loop is None:
            loop = -1
        if name is None or file is None:
            raise RuntimeError("Missing name or file property for music")
        loaded = self.musicMap.get(name, None)
        if loaded is not None:
            return True
        try:
            logger.info(self, "Loading music {name} ({file}, {volume})".format(name=name, file=file, volume=volume))
            snd = sound.Music(self.fmod, name, file, loops=loop, volume=volume, fadeIn=True)
        except Exception as e:
            logger.error(self, "Cannot load music {name} ({file}): {exception}".format(name=name, file=file, exception=e))
            return False
        self.musicMap[name] = snd
        return True
    
    def play(self, name, volume, pan=0.0):
        snd = self.soundMap.get(name, None)
        if snd is not None:
            try:
                snd.play()
                snd.pan(pan)
                return True
            except Exception as e:
                logger.exception(self, "Error playing {name}: {exception}".format(name=name, exception=e), e)
                return False
        else:
            logger.error(self, "Sound {name} is not loaded.".format(name=name))
            return False

    def stop(self, name):
        snd = self.soundMap.get(name, None)
        if snd is not None and snd.isPlaying():
            snd.stop()

    def playMusic(self, name, fadeIn=True):
        music = self.musicMap.get(name, None)
        if music is None:
            logger.error(self, "Music {name} not loaded".format(name=name))
            return False
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
        core.startAnimation()
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
            else:
                newVolume = gameconfig.getValue(m, "volume", float, {"defaultValue": constants.AUDIO_FX_VOLUME})
                if newVolume != self.musicMap[music].getVolume():
                    effects.timeEffects.append(effects.VolumeEffect(self.musicMap[music], newVolume))
                
        return
    
    def event_scene_interval_tick(self, event):
        now = event.get("time", 0)
        if len(effects.timeEffects) == 0:
            core.stopAnimation()
        for effect in effects.timeEffects:
            if isinstance(effect, effects.VolumeEffect):
                # logger.info(self, "Adjusting {name}(volume={volume}, step={step})".format(name=effect.name, volume=effect.curVolume, step=effect.stepValue))
                effect.curVolume += effect.stepValue
                if effect.sound is None or effect.sound.channel is None:
                    effects.timeEffects.remove(effect)
                    continue
                    
                effect.sound.channel.volume = effect.curVolume
                if effect.isCompleted():
                    logger.info(self, "Effect {e} completed".format(e=effect))
                    effects.timeEffects.remove(effect)
                    continue
                effect._lastTick = now
        if self.fmod is not None:
            try:
                self.fmod.update()
            except Exception as e:
                logger.exception(self, "Error updating fMOD: {e}".format(e=e), e)
                
                
def initialize():
    if _instance is None:
        try:
            am = AudioManager()
            return True
        except Exception as e:
            logger.exception("audio", "Error initializing audio: {exception}".format(exception=e), e)
            return False

def play(name, volume=constants.AUDIO_FX_VOLUME, pan=0.0):
    global _instance

    _instance.play(name, volume, pan)
def playMusic(name, fadeIn=True):
    global _instance

    _instance.playMusic(name, fadeIn)


def loadMusic(config):
    global _instance

    return _instance.loadMusic(config)

def stopMusic(name):
    global _instance

    _instance.stopMusic(name)

def computePan(minValue, maxValue, currentValue):
    step = maxValue - minValue
    x = (currentValue - minValue) / step * 2
    ret = 0.0
    if x < 1.0:
        ret = -(1.0 - x)
    elif x > 1.0:
        ret = x - 1.0
    if ret < -0.95:
        ret = -0.95
    elif ret > 0.95:
        ret = 0.95
    return ret
