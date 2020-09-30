# *-* coding: utf8 *-*
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import AppKit
from AppKit import NSSpeechSynthesizer

import speech
import logger
import event_manager
import threading
import queue
import time


THREAD_QUIT = 0xc500585356f8

class SpeechThread(threading.Thread):
    """Underlying thread to monitor speech status and schedule next chunk to speak if any"""
    quit = False
    ss = None
    
    def __init__(self, ss, *args, **kwargs):
        self.msgQueue = queue.Queue()
        super().__init__(*args, **kwargs)
        self.ss = ss

    def run(self):
        self.quit = False
        while self.quit is False:
            if self.ss.isSpeaking() == AppKit.NO:
                try:
                    msg = self.msgQueue.get(block=False)
                except:
                    time.sleep(0.1)
                    continue
                if msg is not None:
                    if msg == THREAD_QUIT:
                        logger.info(self, "Exiting")
                        return True
                    self.ss.startSpeakingString_(msg)
            time.sleep(0.1)

    def cancelSpeech(self):
        self.msgQueue = queue.Queue()
        self.ss.stopSpeaking()

                

class NSSpeech(speech.SpeechSupport):
    ss = None
    statusThread = None
    def __init__(self):
        self.ss = NSSpeechSynthesizer.alloc().init()
        self.statusThread = SpeechThread(self.ss)
        event_manager.addListener(self)
        self.statusThread.start()

    def speak(self, text):
        self.statusThread.msgQueue.put(text)
        logger.info(self, "speak({text})".format(text=text))
    def isActive(self):
        return self.ss != None
    

    def cancelSpeech(self):
        self.statusThread.cancelSpeech()
    def event_quit_game(self, evt):
        self.statusThread.msgQueue.put(THREAD_QUIT)
        self.statusThread.join()
    
    
