# *-* coding: utf-8 *-*

import io, os
import json
import logger

config = None

class GameConfig(object):
    """Loads the engine configuration file and provides methods to get/set config values."""
    config = None
    def __init__(self, file):
        try:
            fileObject = io.FileIO(file)
            data = fileObject.readall()
            fileObject.close()
            self.config = json.loads(data)
            global config
            config = self
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
        return jsonConfig

    def getStartScene(self):
        return self.config.get('start-scene', 'main')
    def getControlResources(self):
        try:
            return self.config["resources"]["controls"]
        except:
            logger.error(self, "No sound resources declared")
            return None

          

    def getLogName(self):
        return "Configuration"
    
            
