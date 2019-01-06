# *-* coding: utf8 *-*

import audio
import logger
import inputHandler

class Scene(object):
    """Defines a scene representing a particular in-game behavior."""

    focused = False
    enterSound = None
    leaveSound = None

    def __init__(self, name, config):
        self.name = name
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
