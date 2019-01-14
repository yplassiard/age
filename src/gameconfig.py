# *-* coding: utf-8 *-*

import io, os, platform, sys
import json
import logger
import constants

_instance = None

class GameConfig(object):
    """Loads the engine configuration file and provides methods to get/set config values."""
    config = None
    def __init__(self, file):
        try:
            fileObject = io.FileIO(file)
            data = fileObject.readall()
            fileObject.close()
            self.config = json.loads(data)
            global _instance
            
            _instance = self
            sys.path.append(self.getLibraryPath())
        except Exception as e:
            logger.error(self, "failed to load file: %s" %(e))
            

    def getSoundResources(self):
        try:
            return self.config["resources"]["sounds"]
        except Exception as e:
            logger.error(self, "No sound resources declared")
            return None

    def getMusicResources(self):
        try:
            return self.config["resources"]["music"]
        except:
            logger.error(self, "No sound resources declared")
            return None


    def getSceneConfiguration(self, name):
        if self.config.get("scenes", None) is None:
            return None
        sceneConfig = self.config["scenes"].get(name, None)
        if isinstance(sceneConfig, dict):
            return sceneConfig
        elif isinstance(sceneConfig, str):
            return self.loadSceneConfiguration(sceneConfig)
    def loadSceneConfiguration(self, jsonFile):
        file = os.path.join(os.path.abspath("."), "data", "scenes", jsonFile)
        try:
            conf = io.FileIO(file)
            jsonConfig = json.load(conf)
        except Exception as e:
            logger.error(self, "Failed to load {file}: {exception}".format(file=jsonFile, exception=e))
            return None
        scenes = jsonConfig.get('scenes', [jsonConfig])
        return scenes

    def getStartScene(self):
        return self.config.get('start-scene', 'main')

    def getPlayerConfig(self):
        return self.config.get('player', None)
    
    def getControlResources(self):
        try:
            return self.config["resources"]["controls"]
        except:
            logger.error(self, "No sound resources declared")
            return None

          

    def getLibraryPath(self):
        return os.path.join(constants.CONFIG_RESOURCE_DIR, platform.system().lower(), platform.architecture()[0])
    
    
    def getLogName(self):
        return "Configuration"
    
            


def getLibraryPath():
    """Returns the path to 3rd party libraries (DLL, DyLib, SO)."""
    global _instance

    if _instance is not None:
        return _instance.getLibraryPath()
    else:
        raise RuntimeError("getLibraryPath(): Configuration not loaded.")

def getPlayerConfig():
    """Returns the player configuration."""
    global _instance

    return _instance.getPlayerConfig()

def getValue(config, key, cls, attrs=None):
    global _instance
    
    className = cls.__name__
    ret = config.get(key, None)
    if ret is None:
        logger.warning(_instance, "Property {key} missing".format(key=key))
        return ret
    if isinstance(ret, cls) is False:
        raise RuntimeError("Configuration error: {key} has to be {clsName}".format(key=key, clsName=className))
    if attrs is None:
        return ret
    minValue = attrs.get("minValue", None)
    maxValue = attrs.get("maxValue", None)
    if minValue is not None and minValue > ret:
        raise RuntimeError("Configuration error: The minimum allowed value for {key} is {min}".format(key=key, min=minValue))
    if maxValue is not None and maxValue < ret:
        raise RuntimeError("Configuration error: The maximum allowed value for {key} is {max}".format(key=key, max=maxValue))

    # list checks
    listCount = attrs.get("elements", None)
    if listCount is not None and isinstance(ret, list) and len(ret) < listCount:
        raise RuntimeError("Configuration error: The {key} list has to contain at least {count} elements".format(key=key, count=listCount))

    # sound and music property checks
    if key.endswith("sound"):
        volume = config.get("%s-volume" % key, constants.AUDIO_DEFAULT_SOUND_VOLUME)
        return (ret, volume)
    if key.endswith("music"):
        volume = config.get("%s-volume" % key, constants.AUDIO_DEFAULT_MUSIC_VOLUME)
        return (ret, volume)
    return ret
