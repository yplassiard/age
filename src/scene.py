# *-* coding: utf-8 *-*

import constants
import core
import eventManager
import inputHandler
import speech
import logger
import audio
import gameconfig

import math

class Scene(object):
  """Defines a scene representing a particular in-game behavior."""
  name = None
  links = {}
  focused = False
  activateSound = None
  deactivateSound = None
  musics = []
  speechName = None
  speechDescription = None

  def __init__(self, name, config):

    if name is None:
      raise RuntimeError("Cannot create a scene without a name")

    self.name = name
    if config is not None:
      self.config = config
      self.activateSound = config.get("enterSound", None)
      self.deactivateSound = config.get("leaveSound", None)
      self.links = config.get("links", {})
      self.speechName = gameconfig.getValue(config, "speech-name", str, {"defaultValue": self.name})
      self.speechDescription = gameconfig.getValue(config, "speech-description", str, {"mandatory": False, "defaultValue": ""})

      self.musics = gameconfig.getValue(config, "musics", list, {"defaultValue": []})
      for music in self.musics:
        music["scene"] = self
        if audio.loadMusic(music) is False:
          logger.warning(self, "Music {name} not loaded".format(name=music.get("name", "unknown")))
          

  def __repr__(self):
    return self.getLogName()
  def getLogName(self):
    return "%s(%s)" %(self.__class__.__name__, self.name)
    
  def getNextScene(self):
    raise NotImplementedError("This scene is terminal.")
  def activate(self, silent=False, params=None):
    if self.focused:
      return True
    self.focused = True
    eventManager.addListener(self)
    logger.info(self, "Scene {name} activated.".format(name=self.name))
    if silent is False and self.activateSound is not None:
      audio.play(self.activateSound)
      
      
    

  def deactivate(self, silent=False):
    if self.focused is False:
      return
    self.focused = False
    eventManager.removeListener(self)
    logger.info(self, "Leaving scene {name}".format(name=self.name))
    if silent is False and self.deactivateSound is not None:
      audio.play(self.deactivateSound)
            

  def describe(self):
    speech.speak("{name}: {description}".format(name=self.speechName, description=self.speechDescription))
    
  def onKeyDown(self, key, mods):
    """Fired when a key is pressed (keyboard or joystick.)"""
        
    action = inputHandler.action(key, mods)
    if action is None:
      return
    script = "input_press_%s" % action
    self.execute(script)
        
  def onKeyUp(self, key, mods):
    """Fired when a key is released (keyboard or joystick)."""
    action = inputHandler.action(key, mods)
    script = "script_release_%s" % action
    self.execute(script)

  def execute(self, script):
    """Finds and executes the given script in the active scene."""
    method = getattr(self, script, None)
    if method:
      try:
        method()
      except Exception as e:
        logger.error(self, "Error executing action {action}: {exception}".format(action=script, exception=e))
        audio.play(constants.AUDIO_ERROR_SOUND)

  def getMusics(self):
    return self.musics
    


class IntervalScene(Scene):
  """Base class that implement a configurable event_interval facility. Each time the interval is
elapsed, the event_interval method will be called.
Note: This event is not called when the scene is not active.
"""
  _interval = 0
  
  def __init__(self, name, config):
    super().__init__(name, config)
    if config:
      self._interval = config.get("interval", None)
      if self._interval is None or isinstance(self._interval, int) is False or self._interval < constants.SCENE_MININUM_INTERVAL:
        msg = "Invalid interval value {value}; has to be integer, minimum is {minValue}".format(value=self._interval, minValue=constants.SCENE_MININUM_INTERVAL)
        logger.error(self, msg)
        raise RuntimeError(msg)
  def activate(self, silent=False, params=None):
    super().activate(silent, params)
    eventManager.post(eventManager.SCENE_INTERVAL_ACTIVATE, {"scene": self})
  def deactivate(self, silent=False):
    eventManager.post(eventManager.SCENE_INTERVAL_DEACTIVATE, {"scene": self})
    super().deactivate(silent)
    
class MenuScene(Scene):
  """This class implements a simple vertical menu.
Each choice is represented as a string or an array of strings, and is defined in the scene
configuration, using the 'choices' attribute. The 'default-choice' attribute instructs the widget
to focus on this particular choice. This value is an index within the choices' list, starting at 
0.
When represented as an array of strings, the first element is considered as a label, subsequent
elements are possible values the user can choose from for this choice. This behavior makes it
possible to implement option selection."""
  choices = []
  default = 0
  idx = 0
  title = None
  speakTitle = True
  choiceIdx = -1
  selectedIdx = -1
  options = {}
  selectSound = None
  selectSoundVolume = 0.8
  validateSound = None
  validateSoundVolume = 0.8
  cancelSound = None
  cancelSoundVolume = 0.8
    
    
  def __init__(self, name, config):
    super().__init__(name, config)
    if config is None:
      return
    self.choices = config.get("choices", None)
    if self.choices is None:
      raise RuntimeError("No menu items provided.")
    self.default = config.get('default-choice', 0)
    if self.default <= 0 or self.default > len(self.choices):
      self.default = 0
    self.idx = self.default
    self.selectedIdx = self.idx
    self.speakTitle = config.get("speak-title", True)
    if self.title is None:
      self.title = config.get('title', 'unknown')
    self.selectSound = config.get('select-sound', None)
    self.selectSoundVolume = config.get("select-sound-volume", constants.AUDIO_FX_VOLUME)
    self.validateSound = config.get('validate-sound', None)
    self.validateSoundVolume = config.get('validate-sound-volume', constants.AUDIO_FX_VOLUME)
    self.cancelSound = config.get('cancel-sound', None)
    self.cancelSoundVolume = config.get('cancel-sound-volume', 0.8)
    self.useStereo = config.get('use-stereo', True)
    
        

    
  def getLogName(self):
    return "MenuScene(%s)" % self.name
    

  def activate(self, silent=False, params=None):
    super().activate(silent)
    if self.speakTitle is True:
      speech.speak(self.title)
    self.speakChoice()

  def input_press_down(self):
    self.idx = (self.idx + 1) % len(self.choices)
    try:
      choice = self.choices[self.idx]
    except Exception as e:
      logger.error(self, "Error reading menu item from list: {exception}".format(exception=e))
      return
    speech.cancelSpeech()
    audio.play(self.selectSound, self.selectSoundVolume, audio.computePan(0, len(self.choices) - 1, self.idx))
    self.speakChoice()

  def input_press_up(self):
    self.idx = (self.idx - 1) % len(self.choices)
    try:
      choice = self.choices[self.idx]
    except:
      return
    speech.cancelSpeech()
    audio.play(self.selectSound, self.selectSoundVolume, audio.computePan(0, len(self.choices) - 1, self.idx))
    self.speakChoice()

  def input_press_right(self):
    if self.choiceIdx != -1:
      self.choiceIdx += 1
      if self.choiceIdx == len(self.choices[self.idx]):
        self.choiceIdx = 1
      self.options[self.idx] = self.choiceIdx
      audio.play(self.selectSound)
      eventManager.post(eventManager.MENU_OPTION_CHANGE, {"optionIndex": self.choiceIdx})
      self.speakChoice()

  def input_press_left(self):
    if self.choiceIdx > 0:
      self.choiceIdx -= 1
      if self.choiceIdx == 0:
        self.choiceIdx = len(self.choices[self.idx]) - 1
      self.options[self.idx] = self.choiceIdx
      audio.play(self.selectSound)
      eventManager.post(eventManager.MENU_OPTION_CHANGE, {"optionIndex": self.choiceIdx})
      self.speakChoice()

  def input_press_action(self):
    audio.play(self.validateSound, self.validateSoundVolume)
    logger.debug(self, "Chosen menu item {name}".format(name=self.choices[self.idx]))
    leaveCurrentScene()
    

  def getNextScene(self):
    """Returns the next scene to activate depending on the user's choice."""
    answer = self.links.get(str(self.idx), None)
    if answer is None:
      audio.play(constants.AUDIO_ERROR_SOUND)
      return
    return answer
  def speakChoice(self):
    try:
      choice = self.choices[self.idx]
      if isinstance(choice, str):
        self.choiceIdx = -1
        speech.speak(choice)
      elif isinstance(choice, list):
        self.choiceIdx = self.options.get(self.idx, 1)
        msg = "{choice}: {selected}".format(choice=choice[0], selected=choice[self.choiceIdx])
        speech.speak(msg)
    except Exception as e:
      logger.error(self, "Failed speak menu itcem: {exception}".format(exception=e))
      return

class StoryTextScene(IntervalScene):
  """A class to present a story text to the user. The text is expected as a list of strings,
  each one read aloud after the other.
  You can configure this widget to scroll the text automatically if the 'interval' key is defined
  to an integer within the scene configuration.
  """
  canSkip = False
  charIdx = 0
  def __init__(self, name, config):
    super().__init__(name, config)
    self.story = self.config.get('story', [])
    self.messageWriteSound = self.config.get('message-write-sound', None)
    self.messageWriteSoundVolume = self.config.get('message-write-sound-volume', 0.8)
    
    if len(self.story) == 0:
      raise RuntimeError("StoryText scene with empty story")
    
  def activate(self, silent=False, params=None):
    self.idx = 0
    self.canSkip = False
    self.charIdx = 0
    super().activate(silent)
    

  def getLogName(self):
    return "StoryTextScene(%s)" % self.name
    

  def speak(self):
    speech.speak(self.story[self.idx])
  def input_press_action(self):
    if not self.canSkip:
      return
    self.idx += 1
    self.canSkip = False
    if self.idx == len(self.story):
      self.charIdx = -1
      leaveCurrentScene()
    else:
      self.charIdx = 0
      
  def getNextScene(self):
    return self.links

  def input_press_up(self):
    if self.canSkip:
      self.speak()
      
  def input_press_down(self):
    if self.canSkip:
      self.speak()

  def event_interval(self):
    if self.charIdx == -1 or self.idx >= len(self.story) or self.charIdx >= len(self.story[self.idx]):
      return
    char = self.story[self.idx][self.charIdx]
    if self.canSkip is False and char not in [" ", "\n", "\r"]:
      audio.play(constants.AUDIO_MESSAGE_SOUND)
    self.charIdx += 1
    if self.charIdx == len(self.story[self.idx]):
      audio.play(constants.AUDIO_MESSAGE_FINISH_SOUND)
      self.canSkip = True
      self.speak()

# Map Scene helper

class MapRegionScene(IntervalScene):
  """Defines a region ef the map where the player can walk into. In such a region, the player can
  walk in four directions, reaching an exit leading to another map region.
  A region is represented as a rectangle.
  """
  height = 0
  width = 0
  regionLinks = None
  playerPosition = None
  walkSounds = []
  runSounds = []
  cameraMode = constants.CAMERA_TOP
  
  isWalking = False
  isRunning = False
  playerMoveTicks = 0
  objectEchoTick = 0
  curAngle = 0
  isTurningLeft = False
  isTurningRight = False
  def __init__(self, name, config):
    config["interval"] = 40
    super().__init__(name, config)
    import sceneManager
    self.player = sceneManager.getPlayer()
    self.height = gameconfig.getValue(config, "height", int, {"minValue": 1})
    self.width = gameconfig.getValue(config, "width", int, {"minValue": 1})
    self.regionLinks = gameconfig.getValue(config, "region-links", list, {"elements": 1})
    self.objectConfigs = gameconfig.getValue(config, "objects", list, {"defaultValue": []})
    self.walkSounds = gameconfig.getValue(config, "walking", list, {"elements": 1, "defaultValue": []})
    cameraModeStr = gameconfig.getValue(config, "default-camera-mode", str, {"defaultValue": "top"})
    if cameraModeStr not in ["top", "subjective"]:
      raise RuntimeError("The camera mode has to be set either to 'top' or 'subjective'.")
    if cameraModeStr == "top":
      self.cameraMode = constants.CAMERA_TOP
    elif cameraModeStr == "subjective":
      self.cameraMode = constants.CAMERA_SUBJECTIVE
    else:
      raise RuntimeError("Unknown camera mode {mode}".format(mode=cameraModeStr))
    
    self.objects = []
    
  def getLogName(self):
    return "MapRegionScene(%s)" % self.name

  def loadObjects(self):
    import objectManager
    ret = True
    for objConfig in self.objectConfigs:
      obj = objectManager.addObject(objConfig)
      if obj is False:
        ret = False
        continue
      if obj is None:
        continue
      objPos = obj.getPosition()
      if objPos is None or isinstance(objPos, list) is False or len(objPos) != 2:
        logger.error(self, "Object({name}) has no position".format(name=obj.name))
        continue
      if objPos[0] <= 0 or objPos[0] >= self.width or objPos[1] <= 0 or objPos[1] >= self.height:
        logger.error(self, "Object({name}, {pos}) position is outside this scene.".format(name=obj.name, pos=objPos))
        continue
      logger.info(self, "{cls}({name}) added to the scene".format(cls=obj.__class__.__name__, name=obj.name))
      self.objects.append(obj)
    if ret is False:
      logger.error(self, "Some objects failed to load.")
    return ret
    
  def getObjects(self):
    return self.objects
  
  def activate(self, silent=False, params=None):
    super().activate(silent, params)
    self.playerPosition = None
    self.sceneTicks = 0
    self.isWalking = False
    self.isRunning = False
    if self.loadObjects() is False:
      logger.warning(self, "Some objects failed to load")
      
    if params is not None:
      enter = params.get('enter', None)
      if enter is not None:
        for region in self.regionLinks:
          if region.get("name", None) == enter:
            pos = gameconfig.getValue(region, "position", list, {"elements": 4})
            msg = "Endering {name} {enter}: {pos}".format(name=self.name, enter=enter, pos=pos)
            logger.debug(self, msg)
            speech.speak(msg)
            if pos[0] == pos[2]:
              self.playerPosition = [pos[0] + 1 if pos[0] == 0 else self.width - 2, pos[1] + int((pos[3] - pos[1]) / 2)]
            elif pos[1] == pos[3]:
              self.playerPosition = [pos[0] + int((pos[2] - pos[0]) / 2), pos[1] + 1 if pos[1] == 0 else self.height - 2]
            else:
              self.playerPosition = [int(self.width / 2), int(self.height / 2)]
      else:
        logger.info(self, "No enter specified, spawning in the middle.")
        self.playerPosition = [int(self.width / 2), int(self.height / 2)]
    else:
      logger.info(self, "No params specified, spawning in the middle.")
      self.playerPosition = [int(self.width / 2), int(self.height / 2)]
    eventManager.post(eventManager.CHARACTER_SPAWN, {"scene": self, "position": self.playerPosition})

  def describe(self):
    self.speechDescription = " ({position})".format(position=self.playerPosition)
    if self.cameraMode == constants.CAMERA_SUBJECTIVE:
      self.speechDescription += ", direction {dir} degrés".format(dir=self.curAngle / constants.DEF_PI_DIVIDE * 180)
    super().describe()
  def event_will_scene_stack(self, evt):
    self.stopMoving()
  

  def input_press_tab(self):
    if self.cameraMode == constants.CAMERA_TOP:
      self.cameraMode = constants.CAMERA_SUBJECTIVE
      speech.speak("Mode subjectif")
      self.curAngle = 80
      eventManager.post(eventManager.AUDIO_CAMERA_CHANGE, {"cameraMode": self.cameraMode})
      eventManager.post(eventManager.AUDIO_RENDER, {"scene": self,
                                                    "listener": self.playerPosition,
                                                    "directionVector": [0.0, 1.0]})
                        
              
    elif self.cameraMode == constants.CAMERA_SUBJECTIVE:
      self.cameraMode = constants.CAMERA_TOP
      speech.speak("Mode vue de dessus")
      self.curAngle = 0
      eventManager.post(eventManager.AUDIO_CAMERA_CHANGE, {"cameraMode": self.cameraMode})
      
      self.stopMoving()
    else:
      logger.error(self, "Unknown camera mode")
    
  def input_press_action(self):
    self.onAction()

  def input_press_shift_up(self):
    self.onWalk(True, constants.DIRECTION_NORTH)

  def input_press_shift_down(self):
    self.onWalk(True, constants.DIRECTION_SOUTH)

  def input_press_shift_right(self):
    self.onWalk(True, constants.DIRECTION_EAST)

  def input_press_shift_left(self):
    self.onWalk(True, constants.DIRECTION_WEST)

  def input_release_shift_up(self):
    self.stopMoving()
  def input_release_shift_down(self):
    self.stopMoving()
  def input_release_shift_left(self):
    self.stopMoving()
  def input_release_shift_right(self):
    self.stopMoving()
  def turnLeft(self):
    self.isTurningLeft = True

  def turnRight(self):
    self.isTurningRight = True
    self.isTurningLeft = False
    
  def input_press_up(self):
    self.onWalk(False, constants.DIRECTION_NORTH)
    
  def input_press_down(self):
    self.onWalk(False, constants.DIRECTION_SOUTH)
    
  def input_press_right(self):
    if self.cameraMode == constants.CAMERA_TOP:
      self.onWalk(False, constants.DIRECTION_EAST)
    else:
      self.turnRight()
      

  def input_press_left(self):
    if self.cameraMode == constants.CAMERA_TOP:
      self.onWalk(False, constants.DIRECTION_WEST)
    elif self.cameraMode == constants.CAMERA_SUBJECTIVE:
      self.turnLeft()
    else:
      logger.error(self, "Unhandled camera mode")
      

  def input_release_up(self):
    self.stopMoving()
  def input_release_down(self):
    self.stopMoving()
  def input_release_left(self):
    self.stopMoving()
  def input_release_right(self):
    self.stopMoving()
  def onWalk(self, running=False, direction=None):
    self.isRunning = running
    if self.isRunning is False:
      self.isWalking = True
    if direction is not None:
      self.direction = direction
    eventManager.post(eventManager.CHARACTER_MOVE, {"direction": self.direction, "type": "run" if running is True else "walk"})
    self.playerMoveTicks = core.currentTicks

  def stopMoving(self):
    self.isRunning = False
    self.isWalking = False
    self.isTurningRight = False
    self.isTurningLeft = False
    self.direction = None
    logger.info(self, "Player stopped moving.")
    
  def event_will_character_move(self, evt):
    eventType = evt.get("type", "walk")
    direction = evt.get("direction", None)
    logger.info(self, "willMore(%s)" % evt)
    if direction is None:
      logger.error(self, "Moving without a direction is not allowed")
      return False # invalid argument
    newPos = self.playerPosition.copy()
    if direction == constants.DIRECTION_NORTH:
      newPos[1] += 1
    elif direction == constants.DIRECTION_SOUTH:
      newPos[1] -= 1
    elif direction == constants.DIRECTION_EAST:
      newPos[0] += 1
    elif direction == constants.DIRECTION_WEST:
      newPos[0] -= 1
    if newPos[0] == 0 or newPos[0] == self.width or newPos[1] == 0 or newPos[1] == self.height:
      eventManager.post(eventManager.CHARACTER_HIT, {"type": "wall"})
      return False
    import objectManager

    objs = objectManager.getNearestObjects(newPos, self.player, self.objects)
    if objs is not None and len(objs) > 0:
      distance,obj = objs[0]
      pos = obj.getPosition()
      size = obj.getSize()
      if newPos[0] > pos[0] - size[0] and newPos[0] < pos[0] + size[0] and newPos[1] > pos[1] - size[1] and newPos[1] < pos[1] + size[1]:
        eventManager.post(eventManager.OBJECT_HIT, {"character": self.player,
                                                    "obj": obj})
        return False
      
      
      
    return True # we can move this character in the desired direction.
  
  def event_character_move(self, evt):
    eventType = evt.get("type", "walk")
    direction = evt.get("direction", None)
    if direction is None:
      logger.error(self, "Moving without a direction is not allowed")
      return
    newPos = self.playerPosition.copy()
    if direction == constants.DIRECTION_NORTH:
      newPos[1] += 1
    elif direction == constants.DIRECTION_SOUTH:
      newPos[1] -= 1
    elif direction == constants.DIRECTION_EAST:
      newPos[0] += 1
    elif direction == constants.DIRECTION_WEST:
      newPos[0] -= 1
      
    # let's see if there is a link to another region
    
    for region in self.regionLinks:
      pos = gameconfig.getValue(region, "position", list, {"elements": 4})
      if (newPos[0] == pos[0] and newPos[1] >= pos[1] and newPos[1] <= pos[3]) \
         or (newPos[1] == pos[1] and newPos[0] >= pos[0] and newPos[0] <= pos[2]):
        scene,enter = region.get("link", "").split(".")
        self.nextScene = scene
        leaveCurrentScene(params={"enter": enter})
        return
    if newPos[0] == 0 or newPos[0] == self.width or newPos[1] == 0 or newPos[1] == self.height:
      return # this is a wall

    # If we reach this nothing prevents us to walk this way        
    self.playerPosition = newPos
    
    # now, let's see what's on this new position

    import objectManager
    objs = objectManager.getNearestObjects(self.playerPosition, self.player, self.objects)
    if objs is not None and len(objs) > 0:
      distance,obj = objs[0] # takes the nearest object
      logger.info(self, "{name} at {distance}".format(name=obj, distance=distance))
      if distance <= obj.getInteractionDistance():
        if obj.onInteract(self, self.player) is True:
          self.stopMoving()
          
    footStepSound = self.getGroundTypeSound()
    audio.play(footStepSound[0], footStepSound[1], audio.computePan(0, self.width, newPos[0]))
        



    

  def event_interval(self):
    import sceneManager
    

    if sceneManager.getActiveScene() != self or core.isInAnimation():
      return
    if self.cameraMode == constants.CAMERA_SUBJECTIVE and (self.isTurningLeft or self.isTurningRight):
      shouldUpdateListener = False
      if self.isTurningLeft:
        self.curAngle += 1
        shouldUpdateListener = True
      elif self.isTurningRight:
        self.curAngle -= 1
        shouldUpdateListener = True
      self.curAngle %= 2 * constants.DEF_PI_DIVIDE
      if shouldUpdateListener:
        dirX = math.cos(self.curAngle * constants.DEF_ANGLE)
        dirY = math.sin(self.curAngle * constants.DEF_ANGLE)
        eventManager.post(eventManager.AUDIO_RENDER, {"scene": self,
                                                      "listener": self.playerPosition,
                                                      "directionVector": [dirX, dirY]})
        
    if (self.isWalking and core.currentTicks - self.playerMoveTicks > constants.HERO_WALK_TIME) or (self.isRunning and core.currentTicks - self.playerMoveTicks > constants.HERO_RUN_TIME):
      self.onWalk(self.isRunning)
    if core.currentTicks - self.objectEchoTick > constants.OBJECT_ECHO_TIME:
      import objectManager
      objs = objectManager.getNearestObjects(self.playerPosition, self.player, self.objects)
      for distance,obj in objs:
        diffY = obj.position[1] - self.playerPosition[1]
        if diffY > 5:
          diffY = 5
        elif diffY < -5:
          diffY = -5
        diffX = (obj.position[0] - self.playerPosition[0]) / 100 * 8
        if diffX <= -0.8:
          diffX = -0.8
        elif diffX >= 0.8:
          diffX = 0.8
        volume = (constants.AUDIO_FX_VOLUME - (distance / self.player.getMaxDistance()) if distance <= self.player.getMaxDistance() else 0)
        if volume <= 0:
          return
        # logger.info(self, "Nearest object {obj} at {distance}, vol={volume}, pitch={pitch}, pan={pan}".format(obj=obj, distance=distance, pitch=diffY, pan=diffX, volume=volume))
        if self.cameraMode == constants.CAMERA_TOP:
          audio.play(obj.getSignalSound(), volume, diffX, pitch=audio.computePitch(0.7, 1.3, diffY))
      self.objectEchoTick = core.currentTicks
      if self.cameraMode == constants.CAMERA_SUBJECTIVE:
        eventManager.post(eventManager.AUDIO_PLAY_3D, {"scene": self})
        
      
  def getGroundTypeSound(self):
    import random
    if self.walkSounds is None or len(self.walkSounds) == 0:
      return
    idx = random.randint(0, len(self.walkSounds) - 1)
    ret = [self.walkSounds[idx], constants.AUDIO_FX_VOLUME]
    return ret
    
            
        
  def getNextScene(self):
    return self.nextScene
  def onAction(self):
    import objectManager
    
    objs = objectManager.getNearestObjects(self.playerPosition, self.player, self.objects)
    if len(objs) > 0:
      distance,obj = objs[0]
      if obj is not None:
        if distance <= obj.getInteractionDistance():
          if obj.onInteract(self, self.player, True) is True:
            self.stopMoving()
  
def leaveCurrentScene(params=None):
    eventManager.post(eventManager.LEAVE_CURRENT_SCENE, {"params": params})

