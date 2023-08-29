# *-* coding: utf-8 *-*
"""
gameconfig
Interface to read and extract values from a engine configuration
"""

import io
import os
import platform
import sys
import json
import logger
import constants

_INSTANCE = None

class GameConfig():
    """Loads the engine configuration file and provides methods to get/set config values."""
    config = None
    def __init__(self, file):
        """constructor"""
        self.file = file
        sys.path.append(self.get_library_path())

    def init(self):
        """Initializes configuration"""
        try:
            file_object = io.FileIO(self.file)
            data = file_object.readall()
            file_object.close()
            self.config = json.loads(data)
            return True
        except Exception as ex:
            logger.error(self, "failed to load file: %s" %(ex))
            return False

    def get_sound_resources(self):
        """retrieves all sound resources"""
        try:
            return self.config["resources"]["sounds"]
        except KeyError:
            logger.error(self, "No sound resources declared")
        return None

    def get_music_resources(self):
        """Retrieves all music resources"""
        try:
            return self.config["resources"]["music"]
        except KeyError:
            logger.error(self, "No sound resources declared")
        return None

    def get_scene_configuration(self, name):
        """Retrieves a specific scene configuration"""
        if self.config.get("scenes", None) is None:
            return None
        scene_config = self.config["scenes"].get(name, None)
        if isinstance(scene_config, dict):
            return scene_config
        if isinstance(scene_config, str):
            return self.load_scene_configuration(scene_config)
        return None

    def load_scene_configuration(self, json_file):
        """Loads a configuration file"""
        file = os.path.join(os.path.abspath("."), "data", "scenes", json_file)
        try:
            conf = io.FileIO(file)
            json_config = json.load(conf)
        except Exception as ex:
            logger.error(self, "Failed to load {file}: {exception}".format(file=json_file, exception=ex))
            return None
        scenes = json_config.get('scenes', [json_config])
        return scenes

    def get_start_scene(self):
        """Returns the scene defined as a start scene"""
        return self.config.get('start-scene', 'main')

    def get_player_config(self):
        """Retrieves the player's configuration"""
        return self.config.get('player', None)

    def get_global_audio_properties(self):
        """Returns the global audio properties"""
        return self.config.get("audio-properties", {})

    def get_control_resources(self):
        """Returns the control (input) resources"""
        try:
            return self.config["resources"]["controls"]
        except KeyError:
            logger.error(self, "No control resources declared")
            return None

    def get_library_path(self):
        """returns library path"""
        return os.path.join(os.path.abspath(constants.CONFIG_RESOURCE_DIR), platform.system().lower(), platform.architecture()[0])

    def get_log_name(self):
        """Returns the name used for logging"""
        return self.__class__.__name__


def initialize(file):
    """Initializes gameconfig singleton"""
    global _INSTANCE
    
    if _INSTANCE is not None:
        return True
    _INSTANCE = GameConfig(file)
    if _INSTANCE and _INSTANCE.init() is True:
        return True
    return False


def get_library_path():
    """Returns the path to 3rd party libraries (DLL, DyLib, SO)."""
    if _INSTANCE is not None:
        return _INSTANCE.get_library_path()
    return ""

def get_player_config():
    """Returns the player configuration."""
    return _INSTANCE.get_player_config()

def get_sound_resources():
    """Gets sound resources"""
    if _INSTANCE is not None:
        return _INSTANCE.get_sound_resources()
    return []


def load_scene_configuration(json_file):
    """Loads a JSON configuration file"""
    if _INSTANCE is not None:
        return _INSTANCE.load_scene_configuration(json_file)
    return None

def get_scene_configuration(name):
    """Gets the dictionnary associated with a scene name"""
    if _INSTANCE is not None:
        return _INSTANCE.get_scene_configuration(name)
    return None

def get_start_scene():
    """Retrieves the start scene"""
    if _INSTANCE is not None:
        return _INSTANCE.get_start_scene()
    return None

def get_value(config, key, cls, attrs=None):
    """Get value from config file"""
    if _INSTANCE is None:
        raise RuntimeError("Game configuration object not initialized")
    if config is None:
        config = _INSTANCE.config
    mandatory = False
    default_value = None
    if attrs is not None:
        mandatory = attrs.get('mandatory', False)
        default_value = attrs.get('defaultValue', None)
    class_name = cls.__name__
    ret = config.get(key, None)
    if ret is None:
        if mandatory is True:
            raise RuntimeError("{key} ppoperty missing".format(key=key))
        return default_value
    if isinstance(ret, cls) is False:
        raise RuntimeError("Configuration error: {key} has to be {clsName}".format(key=key, clsName=class_name))
    if attrs is None:
        return ret
    min_value = attrs.get("minValue", None)
    max_value = attrs.get("maxValue", None)
    if min_value is not None and min_value > ret:
        raise RuntimeError(f"Configuration error: The minimum allowed value for {key} is {min_value}")
    if max_value is not None and max_value < ret:
        raise RuntimeError(f"Configuration error: The maximum allowed value for {key} is {max_value}")

    list_count = attrs.get("elements", None)
    if list_count is not None and isinstance(ret, list) and len(ret) < list_count:
        raise RuntimeError(f"Configuration error: The {key} list has to contain at least {list_count} elements")

    # sound and music property checks
    if key.endswith("sound") or key.endswith("music"):
        volume = get_value(config, "%s-volume" % key, float,
                          {"defaultValue": constants.AUDIO_FX_VOLUME})
        return (ret, volume)
    return ret


def get_global_audio_properties():
    """Returns a dictionary containing audio engine properties."""
    if _INSTANCE is not None:
        return _INSTANCE.get_global_audio_properties()
    return {}
