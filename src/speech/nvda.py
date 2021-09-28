# *-* coding: utf-8 *-*

import ctypes, os
from ctypes import *

import logger
import constants
import gameconfig

import speech
class NVDASupport(speech.SpeechSupport):
	nvdaLibrary = None
	
	def __init__(self):
		path = os.path.join(gameconfig.get_library_path(), "nvdaControllerClient.dll")
		logger.info(self, "Trying to connect to NVDA using {path}".format(path=path))
		self.nvdaLibrary = windll.LoadLibrary(path)
		ret = self.nvdaLibrary.nvdaController_testIfRunning()
		if ret == 0:
			logger.info(self, "Using NVDA as speech output.")
			self.active = True

	def getLogName(self):
		return 'NVDASpeech'

	def isActive(self):
		return self.active
	
	def speak(self, message):
		if self.active is False:
			return
		self.nvdaLibrary.nvdaController_speakText(message)
		logger.info(self, "speak(%s)"% message)
		
	def cancelSpeech(self):
		if self.active is False:
			return
		self.nvdaLibrary.nvdaController_cancelSpeech()
