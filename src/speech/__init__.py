# *-* coding: utf8 *-*
import logger
import platform


class SpeechSupport(object):
        """Base interface for speech support"""
        def speak(self, message):
                raise NotImprementedError
        def cancelSpeech(self):
                raise NotImplementedError
        def terminate(self):
                pass
        def isActive(self):
                return False
        def getLogName(self):
                raise NotImplementedError

_instance = None

def initialize():
        global _instance
        system = platform.system().lower()
        logger.info("speech", "Initialinzing (%s) ..." %(system))
        if system == 'windows':
                # try NVDA first
                from . import nvda
                sr = nvda.NVDASupport()
                if sr.isActive():
                        _instance = sr
                        return True
        elif system == 'darwin':
                from . import nsspeech
                sr = nsspeech.NSSpeech()
                if sr.isActive():
                        _instance = sr
                        return True
        elif system == "linux":
                from . import speech_dispatcher
                try:
                        sr = speech_dispatcher.SPDClient()
                except Exception as e:
                        print(e)
                        raise e
                if sr.isActive():
                        _instance = sr
                        return True
        if _instance is None:
                logger.error("speech", "No speech systems can be initialized.")
                return False

def speak(message):
	global _instance
	if _instance is not None:
		_instance.speak(message)

def cancelSpeech():
	global _instance
	
	if _instance is not None:
		_instance.cancelSpeech()
def terminate():
	global _instance
	
	if _instance is not None:
		_instance.terminate()
def getLogName():
	if _instance is not None:
		return _instance.getLogName()
	else:
		return "speech"
	
