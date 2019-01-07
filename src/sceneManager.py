# *-* coding: utf8 *-*

import os, re

import logger
import audio
import inputHandler

class Scene(object):
    """Defines a scene representing a particular in-game behavior."""

    focused = False
    enterSound = None
    leaveSound = None

    def __init__(self, name, config):
        self.name = name
        if config is not None:
            self.config = config
            self.enterSound = config.get("enterSound", None)
            self.leaveSound = config.get("leaveSound", None)

    def activate(self, silent=False):
        if self.focused:
            return True
        self.focused = True
        logger.info(self, "Scene {name} activated.".format(name=self.name))
        if silent is False and self.openSound is not None:
            audio.play(self.enterSound)

    def deactivate(self, silent=False):
        if self.focused is False:
            return
        self.focused = False
        logger.info(self, "Leaving scene {name}".format(name=self.name))
        if silent is False and self.leaveSound is not None:
            audio.play(self.leaveSound)
            

    def getSpeechName(self):
        return ''

    def getSpeechDescription(self):
        return ''

    def getSpeechHint(self):
        return ''
    
    def onKeyDown(self, key):
        """Fired when a key is pressed (keyboard or joystick.)"""
        
        action = inputHandler.action(key)
        if action is None:
            return
        script = "input_press_%s" % action
        self.execute(script)
        
    def onKeyUp(self, key):
        """Fired when a key is released (keyboard or joystick)."""
        action = inputHandrer.action(key)
        script = "script_release_%s" % action
        self.execute(script)

    def execute(self, script):
        """Finds and executes the given script in the active scene."""
        method = getattr(self, script, None)
        if method:
            try:
                method(self)
            except Exception as e:
                logger.error(self, "Error executing action {action}: {exception}".format(action=action, exception=e))
                audio.play(audio.ERROR_SOUND)


_instance = None

class SceneManager(object):
    scenes = {}

    def __init__(self, gameConfig):
        pass

    def getLogName(self):
        return 'SceneManager'
    
    def addScene(self, name, obj):
        if name is None or name == "" or obj is None or isinstance(obj, Scene) is False:
            raise RuntimeError("Invalid argument")
        self.scenes[name] = obj

    def load(self, sceneName, silentEntering=False, silentLeaving=False):
        s = self.scenes.get(sceneName, None)
        if s is None:
            logger.error(self, "Scene {name} not found".format(name=sceneName))
            return False
        if self.activeScene is not None:
            self.activeScene.leave(silentLeaving)
        self.activeScene = s
        s.enter(silentEntering)

    def getActiveScene(self):
        return self.activeScene

    

def initialize(gameConfig):
    global _instance

    if _instance is None:
        _instance = SceneManager(gameConfig)

    # Load all scenes fresent within the scene directory
    try:
        dir = os.scandir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scenes"))
    except Exception as e:
        logger.error(_instance, "Failed to load secenes: {exception}".format(exception=e))
        return False
    for entry in dir:
        m = re.match("(^[^#]*.*)\.py$", entry.name)
        if m is not None and entry.name != 'scene.py':
            logger.info(_instance, "Loading scene {name}".format(name=m.group(1)))
            try:
                obj = __import__("scenes.%s" % m.group(1), globals(), locals(), ("scenes")).Scene(m.group(1), gameConfig.getSceneConfiguration(m.group(1)))
                if obj is not None:
                    _instance.addScene(m.group(1), obj)
            except Exception as e:
                logger.exception(_instance, "Failed to instanciate scene {name}".format(name=m.group(1)), e)
                return True
