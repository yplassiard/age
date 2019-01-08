# *-* coding: utf-8 *

import io
import pygame

import eventManager

class Logger(object):
    """Log events add information while the game is running."""

    logFile = "a3g-engine.log"
    logIO = None

    def __init__(self, file=None):
        eventManager.addListener(self)
        self.ticks = pygame.time.get_ticks()
        if file is not None:
            self.logFile = file
        try:
            self.logIO = io.FileIO(self.logFile, "a+")
        except:
            print("Failed to open log file: %s" %(self.logFile))
        global _instance
        _instance = self
        self.log("Info", self, "Log system initialized")


    def log(self, category, system, message):
        systemName = None
        if isinstance(system, str):
            systemName = system
        else:
            systemName = system.getLogName()
        try:
            self.logIO.write(bytes("{ticks} {system} {category}: {message}\r\n".format(ticks=pygame.time.get_ticks() - self.ticks, system=systemName, category=category, message=message), 'utf-8'))
            self.logIO.flush()
        except Exception as e:
            print("Log failed: {system} {category}: {message}. Caused by {exception}".format(system=systemName, category=category, message=message, exception=e))
            return False
        return True

    def getLogName(self):
        return 'logger'
    
    def event_quit_game(self, data):
        self.log('Info', self, "Loggging system terminated")
        self.logIO.close()
        self.logIO = None
        global _instance
        _instance = None

_instance = None

def initialize():
    global _instance
    _instance = Logger()

def info(system, message):
    if _instance is not None:
        _instance.log("Info", system, message)
    else:
        print("Log not initialized: {system}: {message}".format(system=system, message=message))


def warning(system, message):
    if _instance is not None:
        _instance.log("Warning", system, message)
    else:
        print("Log not initialized: {system}: {message}".format(system=system, message=message))
def error(system, message):
    if _instance is not None:
        _instance.log("Error", system, message)
    else:
        print("Log not initialized: {system}: {message}".format(system=system, message=message))

