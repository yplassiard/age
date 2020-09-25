# *-* coding: utf-8 *-*
#
# Speech Dispatcher backend for a3g-engine.
#

import speechd
import logger
import speech

class SPDClient(speech.SpeechSupport):
  _module = None
  _voice = None
  _rate = 1.0
  _volume = 1.0
  _pitch = 1.0
  _client = None
  _voices = []

  def getLogName(self):
    return "SpeechDispatcher"
  
  def __init__(self):
    self._client = speechd.Client()
    if self._client is not None:
      self._modules = self._client.list_output_modules()
      for module in self._modules:
        self._client.set_output_module(module)
        self._voices.append({"module": module,
                   "voices": self._client.list_synthesis_voices()})
      self._client.set_language("fr")
      logger.info(self, "Initialized")
    else:
      logger.error(self, "Failed to communicate with Speech Dispatcher")
  def terminate(self):
    del self._client

  def hasLanguageSelectionSupport(self):
    return True
  def setLanguage(self, code):
    if self._client is not None:
      try:
        self._client.set_language(code)
        return True
      except:
        return False
    return False
  def hasVoiceSelectionSupport(self):
    return True
  def listVoices(self):
    voices = []
    for mod in self._voices:
      for voice in mod["voices"]:
        voices.append({"name": "{module} {name}".format(module=mod["module"], name=voice[0]),
                       "id": voice[0],
                       "module": mod,
                       "language": voice[1]})
    return voices
  def selectVoice(self, voice):
    mod = voice.get("module", None)
    id = voice.get("id", None)
    if mod is None or id is None:
      logger.error(self, "Unable to set to voice %s" %(voice))
      return False
    logger.debug(self, "Setting output module to %s, voice to %s" %(mod['module'], id))
    
    self._client.set_output_module(mod['module'])
    self._client.set_synthesis_voice(id)
    self.speak(voice["name"])
    return True
  def speak(self, msg):
    logger.debug(self, "Speak(%s)" %(msg))
    self._client.cancel()
    self._client.say(msg)
  def cancelSpeech(self):
    self._client.cancel()

  def isActive(self):
    return self._client is not None

