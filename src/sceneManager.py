# *-* coding: utf8 *-*

import os, re

import pygame

import constants
import logger
import audio
import inputHandler
import eventManager
import speech
import player
from scene import *

# scene types map from string to real objects.
_sceneTypesMap = {
  "menu": MenuScene,
  "storytext": StoryTextScene,
  "mapregion": MapRegionScene
}

# Global scene manager instance
_instance = None

class SceneManager(object):
  scenes = {}
  intervalScenes = []
  activeScene = None
  player = None
  stack = []
  
  def __init__(self):
    logger.debug(self, "Initializing scene manager.")
    eventManager.addListener(self)
    pc = gameconfig.getPlayerConfig()
    if pc is None:
      raise RuntimeError("No player defined")
    pName = gameconfig.getValue(pc, "name", str)
    
    self.player = player.Player(pName, pc)
    if self.player is None:
      raise RuntimeError("Cannot create player")
    
    
  def getLogName(self):
    return 'SceneManager'

  def createScene(self, config):
    global _sceneTypesMap
        
    type = config.get("type", None)
    name = config.get("name", None)
    cls = _sceneTypesMap.get(type, None)
    if cls is None:
      raise RuntimeError("Scene type {type} is not known.".format(type=type))
    if issubclass(cls, Scene) is False:
      raise RuntimeError("Scene type {type} is not a valid scene type ({realType})".format(type=type, realType=cls.__name__))
    if type is None:
      raise RuntimeError("A scene must have a \"type\" property. Vlid types: {types}".format(types=", ".join([key for key in _sceneTypesMap])))
    logger.debug(self, "Creating scene {cls}({name})".format(cls=cls.__name__, name=name))
    try:
      obj = cls(name, config)
    except Exception as e:
      logger.exception(self, "Error instanciating scene {name}: {exception}".format(name=name, exception=e), e)
      return None
    return obj
    
  def addScene(self, name, obj):
    if name is None or name == "" or obj is None or isinstance(obj, Scene) is False:
      raise RuntimeError("Invalid argument")
    self.scenes[name] = obj
    logger.debug(self, "Registered scene {name}".format(name=name))

  def load(self, sceneName, silentEntering=False, silentLeaving=False, params=None):
    s = self.scenes.get(sceneName, None)
    if s is None:
      logger.error(self, "Scene {name} not found".format(name=sceneName))
      audio.play(constants.AUDIO_ERROR_SOUND)
      return False
    if self.activeScene is not None:
      self.activeScene.deactivate(silentLeaving)
      if params is None:
              params = {}
      params["__parent"] = self.activeScene
      eventManager.post(eventManager.LEAVE_SCENE, {"scene": self.activeScene, "nextScene": s})
    self.activeScene = s
    s.activate(silentEntering, params)
    # key = inputHandler.getLastKeyPressed()
    # if key is not None:
    # self.execute("input_press_%s" % key)
      

  def sceneExists(self, name):
    return True if self.scenes.get(name, None) is not None else False

  def stackScene(self, name):
    s = self.scenes.get(name, None)
    if s is None:
      return False
    if s.name == self.activeScene.name or (len(self.stack) >= 1 and self.stack[-1].name == name):
      logger.error(self, "Cannot stack {name} on top of itself".format(name=s.name))
      return False
    eventManager.post(eventManager.SCENE_STACK, {"scene": s})
    



  def leave(self, silentLeaving=False, params=None):
    if len(self.stack) > 0:
      s = self.stack[-1]
      if len(self.stack) > 2:
        active = self.stack[-2]
      else:
        active = self.activeScene
      eventManager.post(eventManager.SCENE_UNSTACK, {"scene": s, "active": active})
      return
    if self.activeScene is not None:
      nextScene = self.activeScene.getNextScene()
      if nextScene is None:
        return
      if nextScene == '__quit':
        eventManager.post(eventManager.QUIT_GAME)
      else:
        if self.load(nextScene, params=params) is False:
          speech.speak("scene {name} not created yet.".format(name=nextScene))
                    
  def getActiveScene(self):
    if len(self.stack) > 0:
      return self.stack[-1]
    return self.activeScene

  def getPlayer(self):
    return self.player
    

  # events

  def event_leave_scene(self, event):
    if self.activeScene is None:
      eventManager.post(eventManager.QUIT_GAME)


  def event_quit_game(self, event):
    for key in self.scenes:
      self.execute('event_quit_game', target=key)
      self.scenes = {}
      pygame.event.post(pygame.event.Event(pygame.QUIT))

  def event_pause_game(self, event):
    self.execute('event_pause_game', evt, target=self.activeScene)

  def event_leave_current_scene(self, event):
    self.leave(params=event["params"])

  def event_scene_stack(self, event):
    scene = event.get('scene', None)
    if scene is None:
      logger.error(self, "Stacking an empty object is not allowed")
      return False
    self.stack.append(scene)
    scene.activate()

  def event_scene_unstack(self, evt):
    scene = evt.get("scene", None)
    if scene is None:
      logger.error(self, "Unstacking an empty object is not allowed.")
      return False
    scene.deactivate()
    self.stack.remove(scene)
    
  def event_scene_interval_activate(self, event):
    scene = event.get('scene', None)
    if scene is None:
      raise RuntimeError("Invalid call to event_scene_interval_activate without a target scene.")
    scene._nextTick = pygame.time.get_ticks() + scene._interval
    self.intervalScenes.append(scene)

  def event_scene_interval_deactivate(self, event):
    scene = event.get('scene', None)
    if scene is None:
      raise RuntimeError("Invalid call to event_scene_interval_activate without a target scene.")
    idx = 0
    for x in self.intervalScenes:
      if x.name == scene.name:
        self.intervalScenes.pop(idx)
        return
      idx += 1
    logger.error(self, "Failed to remove scene from interval scenes: {name}".format(name=scene.name))

  def event_scene_interval_tick(self, evt):
    now = evt.get('time', 0)
    for x in self.intervalScenes:
      if x._nextTick <= now:
        try:
          x.event_interval()
        except Exception as e:
          logger.exception(self, "Failed to execute {cls}.event_interval: {exception}".format(cls=x.__class__.__name__, exception=e), e)
        x._nextTick = now + x._interval
  def onKeyDown(self, event):
    action = inputHandler.action(event)
    if action is None:
      return False
    return self.execute("input_press_%s" % action)
  def onKeyUp(self, event):
    action = inputHandler.action(event)
    if action is None:
      return False
    return self.execute("input_release_%s" % action)
  def execute(self, script, data=None, target=None):
    if target is None:
      objList = [self]
      if len(self.stack) > 0:
        objList.append(self.stack[-1])
      else:
        objList.append(self.activeScene)
    else:
      objList = [target]
    for obj in objList:
      method = getattr(obj, script, None)
      cls = obj.__class__
      if method is not None:
        try:
          logger.info(self, "Executing {name}.{script}".format(name=cls.__name__, script=script))
          if script.startswith('input'):
            method()
            return
          else:
            method(data)
        except Exception as e:
          logger.error(self, "Failed to execute {name}.{script}: {exception}".format(name=cls.__name__, script=script, exception=e))
          logger.exception(self, "{name}.{script}".format(name=cls.__name__, script=script), e)
          return False

  def input_press_control_shift_l(self):
    self.load("sceneloader")
  def input_press_d(self):
    s = self.getActiveScene()
    if s is not None:
      s.describe()
      
        

def initialize():
  global _instance

  if _instance is None:
    try:
      _instance = SceneManager()
    except Exception as e:
      logger.exception("sceneManager", "Failed to initialize scene manager", e)
      return False
    

  totalScenes = 0
  loadedScenes = 0

  
  try:
    dir = os.scandir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scenes"))
  except Exception as e:
    logger.error(_instance, "Failed to load secenes: {exception}".format(exception=e))
    return False
  for entry in dir:
    m = re.match("(^[^#]+.*)\.py$", entry.name)
    if m is not None and entry.name != 'scene.py':
      logger.info(_instance, "Loading scene {name}".format(name=m.group(1)))
      totalScenes += 1
      try:
        obj = __import__("scenes.%s" % m.group(1), globals(), locals(), ("scenes")).Scene(m.group(1), gameconfig.getSceneConfiguration(m.group(1)))
        if obj is not None:
          _instance.addScene(m.group(1), obj)
          loadedScenes += 1
      except Exception as e:
        logger.exception(_instance, "Failed to instanciate scene {name}: {exception}".format(name=m.group(1), exception=e), e)


  try:
    dir = os.scandir(os.path.join(os.path.abspath("."), "data", "scenes"))
  except Exception as e:
    logger.warning(self, "No user-defined scenes found.")
  if dir is not None:
    for entry in dir:
      m = re.match("(^[^#]+.*)\.json$", entry.name)
      if m is not None:
        try:
          jsonConfigList = gameconfig.loadSceneConfiguration(entry.name)
        except:
          jsonConfigList = None
        if jsonConfigList is None:
          logger.error("sceneManager", "Failed to load scene {name}".format(name=entry.name))
          continue
        for jsonConfig in jsonConfigList:
          totalScenes += 1
          if jsonConfig is not None:
            try:
              obj = _instance.createScene(jsonConfig)
            except Exception as e:
              logger.error(_instance, "Failed to create scene {file}: {exception}".format(file=entry.name, exception=e))
              continue
            if obj is not None:
              _instance.addScene(obj.name, obj)
              loadedScenes += 1
              
        
  if totalScenes > loadedScenes:
    logger.error(_instance, "{count} scenes failed to load".format(count=totalScenes - loadedScenes))

    return False
  logger.info(_instance, "Loaded {count} scenes".format(count=loadedScenes))
  return True

def onKeyDown(event):
  global _instance

  _instance.onKeyDown(event)
  
def onKeyUp(event):
  global _instance

  _instance.onKeyUp(event)

def loadScene(name):
  global _instance
  
  return _instance.load(name)

def sceneExists(name):
  global _instance
  return _instance.sceneExists(name)

def stackScene(name):
  global _instance
  
  return _instance.stackScene(name)

def unstackScene(name):
  global _instance
  
  return _instance.unstackScene(name)

def leaveCurrentScene(params=None):
  global _instance
  
  _instance.leave(params)

def getActiveScene():
  global _instance

  return _instance.getActiveScene()

def getPlayer():
  global _instance
  
  return _instance.getPlayer()
