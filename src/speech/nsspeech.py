# *-* coding: utf8 *-*
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import AppKit
from AppKit import NSSpeechSynthesizer

import speech
import logger

class NSSpeechDelegate(object):
    def didFinishSpeaking(self, sender, finishedSpeaking):
        print("speak finished")

class NSSpeech(speech.SpeechSupport):
    ss = None
    def __init__(self):
        self.ss = NSSpeechSynthesizer.alloc().init()

    def speak(self, text):
        self.ss.startSpeakingString_(text)
        logger.info(self, "speak({text})".format(text=text))
    def isActive(self):
        return self.ss != None
    

    def cancelSpeech(self):
        self.ss.stopSpeaking()
        
    def getLogName(self):
        return "OSXSpeech"
    
