# *-* coding: utf8 *-*

import os, re

import pygame

import logger
import audio
import inputHandler
import eventManager
import speech

class Scene(object):
    """Defines a scene representing a particular in-game behavior."""

    focused = False
    activateSound = None
    deacsjvateSound = None

    def __init__(self, name, config):
        self.name = name
        if config is not None:
            self.config = config
            self.activateSound = config.get("enterSound", None)
            self.deactivateSound = config.get("leaveSound", None)

    def activate(self, silent=False):
        if self.focused:
            return True
        self.focused = True
        logger.info(self, "Scene {name} activated.".format(name=self.name))
        if silent is False and self.activateSound is not None:
            audio.play(self.activateSound)

    def deactivate(self, silent=False):
        if self.focused is False:
            return
        self.focused = False
        logger.info(self, "Leaving scene {name}".format(name=self.name))
        if silent is False and self.deactivateSound is not None:
            audio.play(self.deactivateSound)
            

    def getSpeechName(self):
        return ''

    def getSpeechDescription(self):
        return ''

    def getSpeechHint(self):
        return ''
    
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
                audio.play(audio.ERROR_SOUND)


_instance = None


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
    choiceIdx = -1
    selectedIdx = -1
    options = {}
    
    def __init__(self, name, config):
        super().__init__(name, config)
        if config is not None:
            self.choices = config.get("choices", [])
            self.default = config.get('default-choice', 0)
            if self.default <= 0 or self.default > len(self.choices):
                self.default = 0
            self.idx = self.default
            self.selectedIdx = self.idx
            if config.get('speak-title', False) is True:
                speech.speak(self.title)
            self.speakChoice()

    def getLogName(self):
        return 'menu'
    
    def input_press_down(self):
        self.idx = (self.idx + 1) % len(self.choices)
        try:
            choice = self.choices[self.idx]
        except Exception as e:
            logger.error(self, "Error reading menu item from list: {exception}".format(exception=e))
            return
        speech.cancelSpeech()
        self.speakChoice()

    def input_press_up(self):
        self.idx = (self.idx - 1) % len(self.choices)
        try:
            choice = self.choices[self.idx]
        except:
            return
        speech.cancelSpeech()
        self.speakChoice()

    def input_press_right(self):
        if self.choiceIdx != -1:
            self.choiceIdx += 1
            if self.choiceIdx == len(self.choices[self.idx]):
                self.choiceIdx = 1
            self.options[self.idx] = self.choiceIdx
            self.speakChoice()
    def input_press_left(self):
        if self.choiceIdx != -1:
            self.choiceIdx -= 1
            if self.choiceIdx == 0:
                self.choiceIdx = len(self.choices[self.idx]) - 1
            self.options[self.idx] = self.choiceIdx
            self.speakChoice()
    def input_press_action(self):
        leaveCurrentScene()
        
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
class SceneManager(object):
    scenes = {}
    activeScene = None

    def __init__(self, gameConfig):
        eventManager.addListener(self)

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
            self.activeScene.deactivate(silentLeaving)
        self.activeScene = s
        s.activate(silentEntering)

    def leave(self, silentLeaving=False):
        if self.activeScene is not None:
            self.activeScene.deactivate(silentLeaving)
            eventManager.post(eventManager.LEAVE_SCENE, {"scene": self.activeScene})
            self.activeScene = None
            
    def getActiveScene(self):
        return self.activeScene


    # events

    def event_leave_scene(self, event):
        if self.activeScene is None:
            eventManager.post(eventManager.QUIT_GAME)


    def event_quit_game(self, event):
        for key in self.scenes:
            self.execute('event_quit_game')
        self.scenes = {}
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def event_pause_game(self, event):
        self.execute('event_pause_game', event.data)

    def execute(self, script, data=None):
        if self.activeScene:
            method = getattr(self.activeScene, script)
            if method:
                try:
                    method(data)
                except Exception as e:
                    logger.error(self, "Failed to execute {name}.{script}: {exception}".format(name=self.activeScene.__class__.__name__, script=script, exception=e))


def initialize(gameConfig):
    global _instance

    if _instance is None:
        try:
            _instance = SceneManager(gameConfig)
        except Exception as e:
            logger.error("sceneManager", "Failed to initialize scene manager: {exception}".format(exception=e))
            return False

    # Load all scenes fresent within the scene directory
    totalScenes = 0
    loadedScenes = 0
    try:
        dir = os.scandir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scenes"))
    except Exception as e:
        logger.error(_instance, "Failed to load secenes: {exception}".format(exception=e))
        return False
    for entry in dir:
        m = re.match("(^[^#]*.*)\.py$", entry.name)
        if m is not None and entry.name != 'scene.py':
            logger.info(_instance, "Loading scene {name}".format(name=m.group(1)))
            totalScenes += 1
            try:
                obj = __import__("scenes.%s" % m.group(1), globals(), locals(), ("scenes")).Scene(m.group(1), gameConfig.getSceneConfiguration(m.group(1)))
                if obj is not None:
                    _instance.addScene(m.group(1), obj)
                    loadedScenes += 1
            except Exception as e:
                logger.error(_instance, "Failed to instanciate scene {name}: {exception}".format(name=m.group(1), exception=ee))
    if totalScenes > loadedScenes:
        logger.error(_instance, "{count} scenes failed to load".format(count=totalScenes - loadedScenes))
        return False
    logger.info(_instance, "Loaded {count} scenes".format(count=loadedScenes))
    return True

def onKeyDown(key, mods):
    global _instance
    
    activeScene = _instance.getActiveScene()
    if activeScene is None:
        return
    activeScene.onKeyDown(key, mods)

def onKeyUp(key, mods):
    global _instance

    activeScene = _instance.getActiveScene()
    if activeScene is None:
        return
    activeScene.onKeyUp(key, mods)

def loadScene(name):
    global _instance

    _instance.load(name)

def leaveCurrentScene():
    global _instance

    _instance.leave()
