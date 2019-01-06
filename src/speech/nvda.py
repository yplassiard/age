# *-* coding: utf-8 *-*

import ctypes, os
from ctypes import *

import logger
import speech
class NVDASupport(speech.SpeechSupport):
    nvdaLibrary = None

    def __init__(self):
        self.nvdaLibrary = windll.LoadLibrary(os.path.join("res", "win32", "nvdaControllerClient.dll"))
        ret = self.nvdaLibrary.nvdaController_testIfRunning()
        if ret == 0:
            logger.info(self, "Using NVDA as speech output.")
            self.active = True

    def getLogName(self):
        return 'NVDAClient'

    def isActive(self):
        return self.active
    
    def speak(self, message):
        if self.active is False:
            return
        self.nvdaLibrary.nvdaController_speakText(message)
        
    def cancelSpeech(self):
        if self.active is False:
            return
        self.nvdaLibrary.nvdaController_cancelSpeech()
    
                                         
