# *-* coding: utf8 *-*

import pygame
import constants
import logger
from . import effects

import os



_channels = []

class Sound(object):
	name = None
	snd = None
	channel = None
	playing = False
	initialVolume = constants.AUDIO_FX_VOLUME
	pan = 0.0
	pitch = 1.0

	def __init__(self, fmod, name, file, volume=constants.AUDIO_FX_VOLUME, loop=False, _isMusic=False):
		super().__init__()
		if fmod is None:
			raise RuntimeError("Cannot create a sound without FMOD initialized.")
				
		self.fmod = fmod
		dir = 'sounds'
		if _isMusic:
			dir = 'musics'
		self.name = name
		self.file = file
		self.initialVolume = volume
		self.channel = None
		self._isMusic = _isMusic
		
		try:
			if self._isMusic is False:
				self.snd = self.fmod.create_sound(os.path.join("data", dir, self.file))
			else:
				from .pyfmodex import flags
				self.snd = self.fmod.create_stream(os.path.join("data", dir, self.file), flags.MODE.TWOD | flags.MODE.LOOP_NORMAL)
		except Exception as e:
			logger.error(self, "Unable to load soune: {e}".format(e=e))
			self.snd = None
						
	def setVolume(self, volume, pan=0.0):
		"""Sets the volume and sound panoramic."""
		if self.isPlaying():
			self.channel.volume = volume
			self.channel.position = [pan, 0.0, 1.0]
		self.volume = volume
		self.pan = pan

	def getVolume(self):
		if self.channel is not None:
			return self.channel.volume
		return None

	def getInitialVolume(self):
		"""Returns the initial volume of the sound."""
		return self.initialVolume

	def setInitialVolume(self, volume):
		"""Sets the initial sound volume before applying any volume effect."""
		self.initialVolume = volume
		if self.isPlaying():
			self.channel.volume = self.initialVolume

	def setPitch(self, pitch):
		if self.channel is not None:
			self.channel.pitch = pitch
		self.pitch = pitch
	def getPitch(self):
		if self.channel is not None:
			return self.channel.pitch
		return None
		
	def play(self, paused=False):
		if self.isPlaying():
			self.stop()
		if self.snd is None:
			logger.error(self, "Cannot play a not loaded sound.")
			return False
		try:
			self.channel = self.snd.play(paused=paused)
			# logger.info(self, "Sound started playing {chan}".format(chan=self.channel))
			self.playing = True
			self.channel.position = [self.pan, 1.0, 1.0]
			self.channel.volume = self.volume
			self.channel.pitch = self.pitch
		except Exception as e:
			logger.exception(self, "Error playing {name}: {e}".format(name=self.name, e=e), e)
			return False
		return True
	def setPan(self, value):
		# logger.info(self, "Pan: {value}".format(value=value))
		self.pan = value
		if self.channel is not None:
			self.channel.position = [value, 1.0, 1.0]
			
	def stop(self):
		if self.isPlaying():
			self.channel.stop()
			# logger.info(self, "Stopping sound.")
			self.playing = False
			return True
		return False
	def isPlaying(self):
		if self.channel is None:
			return False
		try:
			self.playing = self.channel.is_playing
			return self.playing
		except:
			self.channel = None
			self.playing = False
			return False
				
		
		

	def getLogName(self):
		return "Sound(%s, %s)" %(self.name, self.file)
def onChannelCB(*args):
		from . import pyfmodex
		logger.info('channel', "Channel callback args: {arg}".format(arg=", ".join(arg for arg in args)))
		return pyfmodex.enums.RESULT.OK

class Music(Sound):
	loops = -1
	def __init__(self, fmod, name, file, volume=constants.AUDIO_MUSIC_VOLUME, loops=-1, snd=None):
		super().__init__(fmod, name, file, volume, snd, _isMusic=True)
		self.loops = loops
		
	def play(self):
		if self.isPlaying():
			return True
		try:
			self.channel = self.snd.play()
			self.channel.loop_count = self.loops
			self.channel.volume = self.initialVolume
			self.playing = True
		except Exception as e:
			logger.error(self, "Failed to play: {e}".format(e=e))
			return False
		return True
	def stop(self, fadeOut=False):
		if self.isPlaying():
			if fadeOut is False:
				self.channel.stop()
				self.channel = None
			else:
				effects.timeEffects.append(effects.VolumeEffect(self, 0.0))
				return True
		return False
		
						
				
	def setFadeIn(self, fadeIn):
		"""Sets the FadeIn Property without affecting the real fade in effect."""
		self.fadeIn = fadeIn
		
