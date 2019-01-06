# *-* coding: utf-8 *-*

import io
import json
import logger

class GameConfig(object):
    """Loads the engine configuration file and provides methods to get/set config values."""
    config = None
    def __init__(self, file):
        try:
            fileObject = io.FileIO(file)
            data = fileObject.readall()
            fileObject.close()
            self.config = json.loads(data)
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


    def getControlResources(self):
        try:
            return self.config["resources"]["controls"]
        except:
            logger.error(self, "No sound resources declared")
            return None

          

    def getLogName(self):
        return "Configuration"
    
            
