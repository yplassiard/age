# *-* coding: utf8 *-*

import AppKit
from AppKit import NSSpeechSynthesizer

import speech

class NSSpeech(speech.SpeechSupport):
    ss = None
    def __init__(self):
        self.ss = NSSpeechSynthesizer.alloc().init()
    def speak(self, text):
        self.ss.startSpeakingString_(text)
    def isActive(self):
        return self.ss != None
    

    def cancelSpeech(self):
        self.ss.stopSpeaking()
        
