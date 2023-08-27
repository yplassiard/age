"""
scene_manager

This modules handles the scene life-time.
"""

# *-* coding: utf8 *-*

import os
import re

import pygame

import constants
import gameconfig
import logger
import audio
import inputHandler
import event_manager
import speech
import player
import scene

# scene types map from string to real objects.

# Global scene manager instance
_INSTANCE = None

class SceneManager():
    """
    This object is responsible for loading, unloading, and managing scenes.
    """
    _sceneTypesMap = {
        "menu": scene.MenuScene,
        "storytext": scene.StoryTextScene,
        "mapregion": scene.MapRegionScene
    }
    _scenes = {}
    _intervalScenes = []
    _active_scene = None
    _player = None
    _stack = []

    def __init__(self):
        """Initializes the scene manager object."""
        logger.debug(self, "Initializing scene manager.")
        event_manager.add_listener(self)
        player_config = gameconfig.get_player_config()
        if player_config is None:
            raise RuntimeError("No player defined")
        player_name = gameconfig.get_value(player_config, "name", str)

        self._player = player.Player(player_name, player_config)
        if self._player is None:
            raise RuntimeError("Cannot create player")


    def get_log_name(self):
        """Returns the name used for logging purposes."""
        return self.__class__.__name__

    def create_scene(self, config):
        """Creates a Scene object from the given configuration."""
        scene_type = config.get("type", None)
        name = config.get("name", None)
        if scene_type is None:
            raise RuntimeError("A scene must have a \"type\" property.")
        cls = self._sceneTypesMap.get(scene_type, None)
        if cls is None:
            raise RuntimeError("Scene type {type} is not known.".format(type=scene_type))
        if issubclass(cls, scene.Scene) is False:
            raise RuntimeError("invalid scene type {type} ({real})".format(type=scene_type,
                                                                           real=cls.__name__))
        logger.debug(self, "Creating scene {cls}({name})".format(cls=cls.__name__, name=name))
        try:
            obj = cls(name, config)
        except Exception as ex:
            logger.exception(self, f"Error instanciating scene {name}", ex)
            return None
        return obj

    def add_scene(self, name, obj):
        """Adds the given scene name with associated object to the collection of
        known scenes.
        """
        if name is None or name == "" or obj is None or isinstance(obj, scene.Scene) is False:
            raise RuntimeError("Invalid argument")
        self._scenes[name] = obj
        logger.debug(self, f"Registered scene {name}")

    def load(self, scene_name, silent_entering=False, silent_leaving=False, params=None):
        """
        Loads the given scene name and make it readyfor activation.
        """
        my_scene = self._scenes.get(scene_name, None)
        if my_scene is None:
            logger.error(self, f"Scene {scene_name} not found")
            audio.play(constants.AUDIO_ERROR_SOUND)
            return False
        if self._active_scene is not None:
            self._active_scene.deactivate(silent_leaving)
            if params is None:
                params = {}
            params["__parent"] = self._active_scene
            event_manager.post(event_manager.LEAVE_SCENE,
                               {"scene": self._active_scene, "nextScene": my_scene})
        self._active_scene = my_scene
        my_scene.activate(silent_entering, params)
        # key = inputHandler.getLastKeyPressed()
        # if key is not None:
        # self.execute("input_press_%s" % key)
        return True

    def scene_exists(self, name):
        """Returns true if the given scene exists, false otherwise."""
        if self._scenes.get(name, None) is not None:
            return True
        return False

    def stack_scene(self, name):
        """Stacks a sceneon top of another one.
        When stacked, the previously active scene is still considered partially active, but do not
        receive events anymore. Its musics and/or akbiant sounds are still mlayed however.
        """
        my_scene = self._scenes.get(name, None)
        if my_scene is None:
            return False
        if my_scene.name == self._active_scene.name \
           or (len(self._stack) >= 1 and self._stack[-1].name == my_scene.name):
            logger.error(self, f"Cannot stack {my_scene.name} on top of itself")
            return False
        event_manager.post(event_manager.SCENE_STACK, {"scene": my_scene})
        return True

    def leave(self, silent_leaving=False, params=None):
        """Leaves the current scene."""
        active_scene = self.get_active_scene()
        next_scene = active_scene.get_next_scene()
        if next_scene == "__unstack" and len(self._stack) > 0:
            if len(self.stack) > 2:
                next_scene = self._stack[-2]
            else:
                next_scene = self._active_scene
            event_manager.post(event_manager.SCENE_UNSTACK,
                               {"scene": active_scene,
                                "active": next_scene,
                                "silent": silent_leaving})
            return
        if next_scene is None:
            return
        if next_scene == '__quit':
            event_manager.post(event_manager.QUIT_GAME)
        elif self.load(next_scene, params=params) is False:
            speech.speak("scene {next_scene} not created yet.")
        else:
            return

    def get_active_scene(self):
        """Returnsthe active scene."""
        if len(self._stack) > 0:
            return self._stack[-1]
        return self._active_scene

    def get_player(self):
        """Returns the main player's object."""
        return self._player


    # events

    def event_leave_scene(self, args):
        """Leaves the given scene."""
        if self._active_scene is None:
            event_manager.post(event_manager.QUIT_GAME)


    def event_quit_game(self, args):
        """Asked to quit the game."""
        for key in self._scenes:
            self.execute('event_quit_game', target=key)
        self._scenes = {}
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def event_pause_game(self, event):
        """Game paused."""
        self.execute('event_pause_game', event, target=self._active_scene)

    def event_leave_current_scene(self, event):
        """We are asked to leave the current scene."""
        self.leave(params=event.get("params", None))

    def event_scene_stack(self, event):
        """Stacks a scene on top of the active one."""
        my_scene = event.get('scene', None)
        if my_scene is None:
            logger.error(self, "Stacking an empty object is not allowed")
            return False
        self._stack.append(my_scene)
        my_scene.activate()
        return True

    def event_scene_unstack(self, evt):
        """Unstacks the latest stacked scene."""
        my_scene = evt.get("scene", None)
        if my_scene is None:
            logger.error(self, "Unstacking an empty object is not allowed.")
            return False
        my_scene.deactivate()
        self._stack.remove(my_scene)
        return True

    def event_scene_interval_activate(self, event):
        """Activates the interval feature for a given scene."""
        my_scene = event.get('scene', None)
        if my_scene is None:
            raise RuntimeError("Invalid call to event_scene_interval_activate without a target scene.")
        my_scene.set_next_tick(pygame.time.get_ticks())
        self._intervalScenes.append(my_scene)

    def event_scene_interval_deactivate(self, event):
        """Deactivates the interval feature for the active scene."""
        my_scene = event.get('scene', None)
        if my_scene is None:
            raise RuntimeError("Invalid call to event_scene_interval_activate without a target scene.")
        idx = 0
        for interval_scene in self._intervalScenes:
            if interval_scene.name == my_scene.name:
                self._intervalScenes.pop(idx)
                return
            idx += 1
        logger.error(self, "Failed to remove scene from interval scenes: {name}".format(name=my_scene.name))

    def event_scene_interval_tick(self, evt):
        """A tick is received to be dispatched tothe active scene, if it implements intervals."""
        now = evt.get('time', 0)
        for interval_scene in self._intervalScenes:
            if interval_scene.get_next_tick() <= now:
                try:
                    interval_scene.event_interval()
                except Exception as ex:
                    logger.exception(self, "Failed to execute {cls}.event_interval: {exception}".format(cls=interval_scene.__class__.__name__, exception=ex), ex)
                interval_scene.set_next_tick(now)
    def on_key_down(self, event):
        """ A key is pressed"""
        action = inputHandler.action(event)
        if action is None:
            return False
        return self.execute("input_press_%s" % action)
    def on_key_up(self, event):
        """Key has been released."""
        action = inputHandler.action(event)
        if action is None:
            return False
        return self.execute("input_release_%s" % action)
    def execute(self, script, data=None, target=None):
        """Executes the given script within an object."""
        if target is None:
            obj_list = [self]
            if len(self._stack) > 0:
                obj_list.append(self._stack[-1])
            else:
                obj_list.append(self._active_scene)
        else:
            obj_list = [target]
        for obj in obj_list:
            method = getattr(obj, script, None)
            cls = obj.__class__
            if method is not None:
                try:
                    logger.info(self, "Executing {name}.{script}".format(name=cls.__name__, script=script))
                    if script.startswith('input'):
                        method()
                        return True
                    method(data)
                except Exception as ex:
                    logger.error(self, "Failed to execute {name}.{script}: {exception}".format(name=cls.__name__, script=script, exception=ex))
                    logger.exception(self, "{name}.{script}".format(name=cls.__name__, script=script), ex)
                    return False
        return False

    def input_press_control_shift_l(self):
        """Invokes the load scene menu."""
        self.load("sceneloader")

    def input_press_d(self):
        """Describe the curren scene."""
        my_scene = self.get_active_scene()
        if my_scene is not None:
            my_scene.describe()



def initialize():
    """Initializes this component, loading all scenes."""
    global _INSTANCE

    if _INSTANCE is None:
        try:
            _INSTANCE = SceneManager()
        except Exception as ex:
            logger.exception("scene_manager", "Failed to initialize scene manager", ex)
            return False


    total_scenes = 0
    loaded_scenes = 0

    try:
        my_dir = os.scandir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scenes"))
    except Exception as ex:
        logger.error(_INSTANCE, "Failed to load secenes: {exception}".format(exception=ex))
        return False
    for entry in my_dir:
        match = re.match(r"(^[^#]+.*)\.py$", entry.name)
        if match is not None and entry.name != 'scene.py':
            logger.info(_INSTANCE, "Loading scene {name}".format(name=match.group(1)))
            total_scenes += 1
            try:
                module = __import__("scenes.%s" % match.group(1), globals(), locals(), ("scenes"))
                obj = module.Scene(match.group(1), gameconfig.get_scene_configuration(match.group(1)))
                if obj is not None:
                    _INSTANCE.add_scene(match.group(1), obj)
                    loaded_scenes += 1
            except Exception as ex:
                logger.exception(_INSTANCE, f"Failed to instanciate scene {match.group(1)}", ex)


    try:
        my_dir = os.scandir(os.path.join(os.path.abspath("."), "data", "scenes"))
    except Exception as ex:
        logger.warning("scene_manager", "No user-defined scenes found.")
    if my_dir is not None:
        for entry in my_dir:
            match = re.match(r"(^[^#]+.*)\.json$", entry.name)
            if match is not None:
                try:
                    json_config_list = gameconfig.load_scene_configuration(entry.name)
                except Exception as ex:
                    json_config_list = None
                if json_config_list is None:
                    logger.error("scene_manager", "Failed to load scene {name}".format(name=entry.name))
                    continue
                for json_config in json_config_list:
                    total_scenes += 1
                    if json_config is not None:
                        try:
                            obj = _INSTANCE.create_scene(json_config)
                        except Exception as ex:
                            logger.error(_INSTANCE, "Failed to create scene {file}: {exception}".format(file=entry.name, exception=ex))
                            continue
                        if obj is not None:
                            _INSTANCE.add_scene(obj.name, obj)
                            loaded_scenes += 1

    if total_scenes > loaded_scenes:
        logger.error(_INSTANCE, "{count} scenes failed to load".format(count=total_scenes - loaded_scenes))

        return False
    logger.info(_INSTANCE, "Loaded {count} scenes".format(count=loaded_scenes))
    return True

def on_key_down(event):
    """Key ispressed."""
    global _INSTANCE

    _INSTANCE.on_key_down(event)

def on_key_up(event):
    """A key is released."""
    global _INSTANCE

    _INSTANCE.on_key_up(event)

def load_scene(name):
    """Loads the given scene name."""
    global _INSTANCE

    return _INSTANCE.load(name)

def scene_exists(name):
    """Returns true if scene exists, false otherwise."""
    global _INSTANCE
    return _INSTANCE.scene_exists(name)

def stack_scene(name):
    """Stacks a scene."""
    global _INSTANCE

    return _INSTANCE.stack_scene(name)

def unstack_scene():
    """Unstacks the given scene."""
    global _INSTANCE

    return _INSTANCE.leave()

def leave_current_scene(params=None):
    """Leave the current scene."""
    global _INSTANCE

    _INSTANCE.leave(params)

def get_active_scene():
    """Returns the currently active scene."""
    global _INSTANCE

    return _INSTANCE.get_active_scene()

def get_player():
    """Returns the player's object."""
    global _INSTANCE

    return _INSTANCE.get_player()
