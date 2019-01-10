# *-* coding: utf8 *-*

import constants
import eventManager
import inputHandler
import speech
import logger
import audio
import gameconfig


class Scene(object):
    """Defines a scene representing a particular in-game behavior."""
    name = None
    links = {}
    focused = False
    activateSound = None
    deactivateSound = None

    def __init__(self, name, config):
        if name is None:
            raise RuntimeError("Cannot create a scene without a name")
        self.name = name
        if config is not None:
            self.config = config
            self.activateSound = config.get("enterSound", None)
            self.deactivateSound = config.get("leaveSound", None)
            self.links = config.get("links", {})

    def getNextScene(self):
        raise NotImplementedError("This scene is terminal.")
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
                audio.play(constants.AUDIO_ERROR_SOUND)




class IntervalScene(Scene):
    """Base class that implement a configurable event_interval facility. Each time the interval is
elapsed, the event_interval method will be called.
Note: This is event is not called when the scene is not active.
"""
    _interval = 0

    def __init__(self, name, config):
        super().__init__(name, config)
        if config:
            self._interval = config.get("interval", None)
            if self._interval is None or isinstance(self._interval, int) is False or self._interval < constants.SCENE_MININUM_INTERVAL:
                raise RuntimeError("Invalid interval value {value}".format(self._interval))
    def activate(self, silent=False):
        super().activate(silent)
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
    title = 'Unknown'
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
        self.title = config.get('title', 'unknown')
        self.selectSound = config.get('select-sound', None)
        self.selectSoundVolume = config.get("select-sound-volume", 0.8)
        self.validateSound = config.get('validate-sound', None)
        self.validateSoundVolume = config.get('validate-sound-volume', 0.8)
        self.cancelSound = config.get('cancel-sound', None)
        self.cancelSoundVolume = config.get('cancel-sound-volume', 0.8)
        self.useStereo = config.get('use-stereo', True)

        

    
    def getLogName(self):
        return 'menu'

    def activate(self, silent=False):
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
            self.speakChoice()

    def input_press_left(self):
        if self.choiceIdx != -1:
            self.choiceIdx -= 1
            if self.choiceIdx == 0:
                self.choiceIdx = len(self.choices[self.idx]) - 1
            self.options[self.idx] = self.choiceIdx
            audio.play(self.selectSound)
            self.speakChoice()

    def input_press_action(self):
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
to an integer within the scene configuration."""
    canSkip = False
    charIdx = 0
    def __init__(self, name, config):
        super().__init__(name, config)
        self.story = self.config.get('story', [])
        self.messageWriteSound = self.config.get('message-write-sound', None)
        self.messageWriteSoundVolume = self.config.get('message-write-sound-volume', 0.8)
        
        if len(self.story) == 0:
            raise RuntimeError("StoryText scene with empty story")

    def activate(self, silent=False):
        self.idx = 0
        self.canSkip = False
        self.charIdx = 0
        super().activate(silent)


    def getLogName(self):
        return 'StoryText'

    def speak(self):
        speech.speak(self.story[self.idx])
    def input_press_action(self):
        if not self.canSkip:
            return
        self.idx += 1
        self.canSkip = False
        if self.idx == len(self.story):
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
        if self.canSkip is False:
            audio.play(constants.AUDIO_MESSAGE_SOUND)
        self.charIdx += 1
        if self.charIdx == len(self.story[self.idx]):
            audio.play(constants.AUDIO_MESSAGE_FINISH_SOUND)
            self.canSkip = True
            self.speak()    
        
        
    
    
        


def leaveCurrentScene():
    eventManager.post(eventManager.LEAVE_CURRENT_SCENE)
