# *-* coding: utf-8 *-*

import io, os, platform, sys
import json
import logger
import constants

_instance = None

class GameConfig():
    """Loads the engine configuration file and provides methods to get/set config values."""
    config = None
    def __init__(self, file):
        self.file = file
        sys.path.append(self.get_library_path())
    def init(self):
        try:
            fileObject = io.FileIO(self.file)
            data = fileObject.readall()
            fileObject.close()
            self.config = json.loads(data)
            return True
        except Exception as ex:
            logger.error(self, "failed to load file: %s" %(ex))
            return False

    def get_sound_resources(self):
        try:
            return self.config["resources"]["sounds"]
        except KeyError as ex:
            logger.error(self, "No sound resources declared")
        return None

    def get_music_resources(self):
        try:
            return self.config["resources"]["music"]
        except KeyError:
            logger.error(self, "No sound resources declared")
        return None

    def get_scene_configuration(self, name):
        if self.config.get("scenes", None) is None:
            return None
        scene_config = self.config["scenes"].get(name, None)
        if isinstance(scene_config, dict):
            return scene_config
        if isinstance(scene_config, str):
            return self.load_scene_configuration(scene_config)
        return None
    def load_scene_configuration(self, json_file):
        file = os.path.join(os.path.abspath("."), "data", "scenes", json_file)
        try:
            conf = io.FileIO(file)
            json_config = json.load(conf)
        except Exception as ex:
            logger.error(self, "Failed to load {file}: {exception}".format(file=jsonFile, exception=ex))
            return None
        scenes = json_config.get('scenes', [json_config])
        return scenes

    def get_start_scene(self):
        return self.config.get('start-scene', 'main')

    def get_player_config(self):
        return self.config.get('player', None)

    def get_global_audio_properties(self):
        return self.config.get("audio-properties", {})

    def get_control_resources(self):
        try:
            return self.config["resources"]["controls"]
        except KeyError:
            logger.error(self, "No control resources declared")
            return None

    def get_library_path(self):
        return os.path.join(os.path.abspath(constants.CONFIG_RESOURCE_DIR), platform.system().lower(), platform.architecture()[0])

    def get_log_name(self):
        return self.__c;ass__.__name__


def initialize(file):
  global _instance

  if _instance is not None:
    return True
  _instance = GameConfig(file)
  if _instance and _instance.init() is True:
    return True
  return False


def get_library_path():
    """Returns the path to 3rd party libraries (DLL, DyLib, SO)."""
    global _instance
    if _instance is not None:
        return _instance.get_library_path()
    return ""

def get_player_config():
    """Returns the player configuration."""
    global _instance
    return _instance.get_player_config()

def get_sound_resources():
    global _instance

    if _instance is not None:
        return _instance.get_sound_resources()
    return []

def load_scene_configuration(json_file):
    global _instance

    if _instance is not None:
        return _instance.load_scene_configuration(json_file)
    return None

def get_scene_configuration(name):
    global _instance

    if _instance is not None:
        return _instance.get_scene_configuration(name)
    return None

def get_start_scene():
    global _instance

    if _instance is not None:
        return _instance.get_start_scene()
    return None

def get_value(config, key, cls, attrs=None):
    global _instance
    if _instance is None:
        raise RuntimeError("Game configuration object not initialized")
    if config is None:
        config = _instance.config
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
        raise RuntimeError("Configuration error: The minimum allowed value for {key} is {min}".format(key=key, min=min_value))
    if max_value is not None and max_value < ret:
        raise RuntimeError("Configuration error: The maximum allowed value for {key} is {max}".format(key=key, max=max_value))

    list_count = attrs.get("elements", None)
    if list_count is not None and isinstance(ret, list) and len(ret) < list_count:
        raise RuntimeError("Configuration error: The {key} list has to contain at least {count} elements".format(key=key, count=list_count))

    # sound and music property checks
    if key.endswith("sound") or key.endswith("music"):
        volume = getValue(config, "%s-volume" % key, float, {"defaultValue": constants.AUDIO_DEFAULT_SOUND_VOLUME})
        return (ret, volume)
    return ret


def get_global_audio_properties():
    """Returns a dictionary containing audio engine properties."""
    global _instance

    if _instance is not None:
        return _instance.get_global_audio_properties()
    return {}
