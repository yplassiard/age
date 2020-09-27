# *-* coding: utf-8 *

import io
import pygame
import sys
import traceback

import eventManager


"""Log Categories defines, for each component, the level we want to log."""
_logComponents = {
  "sceneManager": 100,
  "SpeechDispatcher": 100,
  "eventManager": 100,
}

class Logger(object):
  """Log events add information while the game is running."""

  logFile = "age.log"
  logIO = None
  name = 'logger'

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
    # sys.stdout = self
    # sys.stderr = self


  def log(self, category, system, message):
    global _logComponents
    
    level = 0
    if category == "Error":
      level   = 1
    elif category == 'Warning':
      level = 10
    elif category == 'Notice':
      level = 20
    elif category == 'Info':
      level = 30
    elif category == 'Debug':
      level = 40
    else:
      level = 50
    systemName = None
    if isinstance(system, str):
      systemName = system
    else:
      try:
        systemName = system.getLogName()
      except:
        systemName = system.__class__.__name__
    logLevel = _logComponents.get(systemName, 30)
    if logLevel < level:
      return
    try:
      self.logIO.write(bytes("{ticks} {system} {category}: {message}\r\n".format(ticks=pygame.time.get_ticks() - self.ticks, system=systemName, category=category, message=message), 'utf-8'))
      # self.logIO.flush()
    except Exception as e:
      print("Log failed: {system} {category}: {message}. Caused by {exception}".format(system=systemName, category=category, message=message, exception=e))
      return False
    return True

  def getLogName(self):
    return 'logger'

  def getLogIO(self):
    return self.logIO

  def write(self, msg):
    self.log("Warning", 'console', msg.rstrip("\n"))
    return len(msg)

  def flush(self):
    self.logIO.flush()
    
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
def debug(system, message):
  global _instance
  
  if _instance is not None:
    _instance.log("Debug", system, message)
  else:
    print("D: {system}: {message}".format(system=system, message=message))

  
def info(system, message):
  global _instance
  
  if _instance is not None:
    _instance.log("Info", system, message)
  else:
    print("I: {system}: {message}".format(system=system, message=message))

def notice(system, message):
  global _instance
  
  if _instance is not None:
    _instance.log("Notice", system, message)
  else:
    print("N: {system}: {message}".format(system=system, message=message))


def warning(system, message):
  global _instance
  
  if _instance is not None:
    _instance.log("Warning", system, message)
  else:
    print("W: {system}: {message}".format(system=system, message=message))

def error(system, message):
  global _instance

  if _instance is not None:
    _instance.log("Error", system, message)
  else:
    print("E: {system}: {message}".format(system=system, message=message))



def exception(system, message, exception):
        global _instance
        if _instance is not None:
                msg = "{message}: {exception}".format(message=message, exception=exception)
                import speech
                try:
                        speech.speak(msg)
                except:
                         pass
                _instance.log("Exception", system, msg)
                print("Exception", system, msg)
                traceback.print_tb(exception.__traceback__)
        else:
                print("Log not initialized: {system}: {message}".format(system=system, message=message))

