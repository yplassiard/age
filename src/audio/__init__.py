# *-* coding: utf-8 *-*

import logger
import constants
import core
import gameconfig
import event_manager
import pygame
import os

from . import effects
from . import sound


# Audio subsystem




_instance = None



class AudioManager():
    """Manages all audio resources (sfx, bgm)"""
    soundMap = {}
    musicMap = {}
    fmod = None

        
    def __init__(self, config):
        """Initializes the AudioManager with the help of L{GameConfig} object."""
        event_manager.add_listener(self)
        try:
            from . import pyfmodex
            self.fmod = pyfmodex.System()
            self.fmod.init()
            self.listener = self.fmod.listener()
            self.listener.position = [0.0, 0.0, 0.0]
        except Exception as e:
            logger.exception(self, "Failed to load FMOD library: {e}".format(e=e), e)
            raise e
        self.fadeInterval = gameconfig.get_value(config, "fade-interval", int, {"defaultValue": constants.AUDIO_FADE_INTERVAL, "minValue": 1})
        self.fadeTicks = 0
        self.stereoWidth = gameconfig.get_value(config, "stereo-field-width", int, {"defaultValue": constants.AUDIO_STEREO_FIELD_WIDTH, "minValue": 30, "maxValue": 100})
        self.stereoWidth /= 100
        for s in gameconfig.get_sound_resources():
            logger.info(self, "Loading {name} ({file})".format(name=s["name"], file=s["file"]))
            try:
                snd = sound.Sound(self.fmod, s["name"], s["file"])
                self.soundMap[s["name"]] = snd
            except Exception as e:
                logger.exception(self, "Failed to load {file}: {exception}".format(file=s["file"], exception=e), e)
        global _instance

        _instance = self

    def loadMusic(self, config):
        name = gameconfig.get_value(config, "name", str)
        file = gameconfig.get_value(config, "file", str)
        loop = gameconfig.get_value(config, "loops", int, {"defaultValue": -1})
        volume = gameconfig.get_value(config, "initial-volume", float, {"minValue": 0.0,
                                                                                                                                     "maxValue": 1.0,
                                                                                                                                     "defaultValue": 0.0})
    
        if loop is None:
            loop = -1
        if name is None or file is None:
            raise RuntimeError("Missing name or file property for music")
        loaded = self.musicMap.get(name, None)
        if loaded is not None:
            return True
        try:
            logger.info(self, "Loading music {name} ({file}, {volume})".format(name=name, file=file, volume=volume))
            snd = sound.Music(self.fmod, name, file, loops=loop, volume=volume)
        except Exception as e:
            logger.error(self, "Cannot load music {name} ({file}): {exception}".format(name=name, file=file, exception=e))
            return False
        self.musicMap[name] = snd
        return True
        
    def play(self, name, volume, pan=0.0, pitch=1.0):
        snd = self.soundMap.get(name, None)
        if snd is not None:
            try:
                snd.setVolume(volume)
                snd.setPan(pan)
                snd.setPitch(pitch)
                snd.play(paused=False)
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

    def playMusic(self, name):
        music = self.musicMap.get(name, None)
        if music is None:
            logger.error(self, "Music {name} not loaded".format(name=name))
            return False
        music.play()
        
    def stopMusic(self, name):
        music = self.musicMap.get(name, None)
        if music is not None:
            music.stop()
            
    def get_log_name(self):
        return "AudioManager"



    def event_leave_scene(self, event):
        core.start_animation()
        my_scene = event.get("scene", None)
        if my_scene is None:
            return
        next_scene = event.get('nextScene', None)
        if next_scene is None:
            next_scene_music = []
        else:
            next_scene_music = next_scene.get_musics()
        for music in self.musicMap:
            found = False
            musicConfig = None
            for m in next_scene_music:
                if m["name"] == music:
                    found = True
                    musicConfig = m
            snd = self.musicMap[music]                
            if not found:
                if snd.isPlaying():
                    logger.info(self, "stopping {music}".format(music=music))
                    self.musicMap[music].stop(fadeOut=True)
            else:
                newVolume = gameconfig.get_value(musicConfig, "volume", float, {"defaultValue": constants.AUDIO_FX_VOLUME})
                initialVolume = gameconfig.get_value(musicConfig, "initial-volume", float, {"defaultValue": 0.0})
                    
                if snd.isPlaying() is False:
                    snd.play()
                if snd.getInitialVolume() != initialVolume:
                    snd.setVolume(initialVolume)
                if newVolume != snd.getVolume():
                    logger.info(self, "Scheduling {music} to new volume {newVolume}".format(music=music, newVolume=newVolume))
                    effects.timeEffects.append(effects.VolumeEffect(self.musicMap[music], newVolume))
                    


    def event_audio_camera_change(self, evt):
        mode = evt.get("cameraMode", None)
        if mode is None:
            logger.error(self, "Missing audio camera mode")
            return True
        if mode == constants.CAMERA_TOP:
            self.listener.position = [0.0, 0.0, 0.0]
    
    def event_audio_render(self, evt):
        scene = evt.get("scene", None)
        listenerPos = evt.get("listener", None)
        dirVector = evt.get("directionVector", None)
        if scene is None or listenerPos is None or dirVector is None:
            logger.error(self, "cannot render, missing scene or listener position")
            return False
        for obj in scene.getObjects():
            soundStr = obj.getSignalSound()
            snd = self.soundMap.get(soundStr, None)
            if snd is not None:
                snd.set3DCoordinates(obj.position[0], obj.position[1], 1.0)
                # snd.setMinMaxDistance(obj.getDistances())
        self.listener.position = [listenerPos[0], 1.0, listenerPos[1]]
        self.listener.forward = [dirVector[0], 0.0, dirVector[1]]
        self.listener.up = [0.0, 1.0, 0.0]
        self.listener.velocity = [0.0, 0.0, 0.0]
        

    def event_audio_play_3d(self, evt):
        scene = evt.get("scene", None)
        if scene is None:
            logger.error(self, "Failed to play 3D sounds without a scene")
            return True
        for obj in scene.getObjects():
            signalSoundStr = obj.getSignalSound()
            snd = self.soundMap.get(signalSoundStr, None)
            if snd:
                snd.play() # position is already set.
        # self.fmod.update()

    def event_stack_scene(self, evt):
        scene = evt.get("scene", None)
        sceneMusics = scene.getSceneMusics()
        if sceneMusics is None or len(sceneMusics) == 0:
            return
        for music in sceneMusics:
            snd = self.musicMap.get(music["name"], None)
            if snd is None:
                logger.error(self, "stack({name}): Music {music} not found.".format(name=scene.name, music=music["name"]))
                continue
            snd.play()
    def event_unstack_scene(self, evt):
        scene = evt.get("scene", None)
        active = evt.get("active", None)
        if active     is None:
            activeMusics = []
        else:
            activeMusics = active.getMusics()
        if scene is None:
            logger.error(self, "unstack(): No scene specified.")
            return
        return
        
        
                        
                        
                
                
    def event_scene_interval_tick(self, event):
        now = event.get("time", 0)
        if len(effects.timeEffects) == 0:
            core.stop_animation()
        if core.get_current_ticks() - self.fadeTicks > self.fadeInterval:
            self.fadeTicks = core.get_current_ticks()
            for effect in effects.timeEffects:
                if isinstance(effect, effects.VolumeEffect):
                    # logger.info(self, "{x} Adjusting {name}(volume={volume}, step={step})".format(x=len(effects.timeEffects), name=effect.name, volume=effect.curVolume, step=effect.stepValue))
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
                
                
def initialize(config):
    if _instance is None:
        try:
            am = AudioManager(config)
            return True
        except Exception as e:
            logger.exception("audio", "Error initializing audio: {exception}".format(exception=e), e)
        return False
    else:
        return True
        
def play(name, volume=constants.AUDIO_FX_VOLUME, pan=0.0, pitch=1.0):
        global _instance

        _instance.play(name, volume, pan, pitch=pitch)
def playMusic(name):
        global _instance

        _instance.playMusic(name)


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
        if ret < -_instance.stereoWidth:
                ret = -_instance.stereoWidth
        elif ret > _instance.stereoWidth:
                ret = _instance.stereoWidth
        return ret
def computePitch(minValue, maxValue, curValue):
    step = maxValue - minValue
    ret = 1 + (curValue / 100 * 2)
    return ret
