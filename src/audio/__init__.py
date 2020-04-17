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
			raise e
				
		for s in gameconfig.getSoundResources():
			logger.info(self, "Loading {name} ({file})".format(name=s["name"], file=s["file"]))
			try:
				snd = sound.Sound(self.fmod, s["name"], s["file"])
				self.soundMap[s["name"]] = snd
			except Exception as e:
				logger.exception(self, "Failed to load {file}: {exception}".format(file=s["file"], exception=e), e)
		self.stereoWidth = gameconfig.getValue(None, "stereo-field-width", int, {"defaultValue": 95, "minValue": 30, "maxValue": 100})
		self.stereoWidth /= 100
		global _instance

		_instance = self

	def loadMusic(self, config):
		name = gameconfig.getValue(config, "name", str)
		file = gameconfig.getValue(config, "file", str)
		loop = gameconfig.getValue(config, "loops", int, {"defaultValue": -1})
		volume = gameconfig.getValue(config, "initial-volume", float, {"minValue": 0.0,
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
				snd.play()
				snd.setVolume(volume)
				snd.pan(pan)
				snd.setPitch(pitch)
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
			
	def getLogName(self):
		return "AudioManager"



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
			musicConfig = None
			for m in nextSceneMusic:
				if m["name"] == music:
					found = True
					musicConfig = m
			snd = self.musicMap[music]				
			if not found:
				if snd.isPlaying():
					logger.info(self, "stopping {music}".format(music=music))
					self.musicMap[music].stop(fadeOut=True)
			else:
				newVolume = gameconfig.getValue(musicConfig, "volume", float, {"defaultValue": constants.AUDIO_FX_VOLUME})
				initialVolume = gameconfig.getValue(musicConfig, "initial-volume", float, {"defaultValue": 0.0})
					
				if snd.isPlaying() is False:
					snd.play()
				if snd.getInitialVolume() != initialVolume:
					snd.setVolume(initialVolume)
				if newVolume != snd.getVolume():
					logger.info(self, "Scheduling {music} to new volume {newVolume}".format(music=music, newVolume=newVolume))
					effects.timeEffects.append(effects.VolumeEffect(self.musicMap[music], newVolume))
					


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
		if active	 is None:
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
			core.stopAnimation()
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
				
				
def initialize():
	if _instance is None:
		try:
			am = AudioManager()
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
