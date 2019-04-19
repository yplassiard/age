# *-* coding: utf8 *-*

import constants
import gameconfig
import logger
import eventManager
from objects import Object

class Player(Object):
    health = None
    stamina = None
    magic = None
    maxDistance = None

    def __init__(self, name, config):
        super().__init__(name, config)
        eventManager.addListener(self)
        self.health = gameconfig.getValue(config, "health", int, {"minValue": 1})
        self.magic = gameconfig.getValue(config, "magic", int, {})
        self.stamina = gameconfig.getValue(config, "stamina", int, {"minValue": 1})
        self.maxDistance = gameconfig.getValue(config, "max-distance", float, {"defaultValue": 5})
        self.inventory = self.loadInventory(config.get("inventory", None))
    def loadInventory(self, inventory):
        if inventory is None:
            return True
        for name in inventory:
            obj = objectManager.get(name)
            if obj is not None:
                self.inventory.append(obj)
            else:
                logger.error(self, "Cannot add {name} to inventory: object not found.".format(name=name))
                return False
        return True
    
    
                

    def getMaxDistance(self):
        """Returns the maximum distance the player can ear sounds from."""
        return self.maxDistance
    
    
                   

    def getLogName(self):
        return "Player(%s)" % self.name
    
    # events

    def event_hero_walk(self, evt):
        logger.info(self, "Walking ({posX}, {posY})".format(posX=evt["position"][0], posY=evt["position"][1]))
        
    def event_hero_run(self, evt):
        pass

    def event_hero_spawn(self, evt):
        s = evt.get("scene", None)
        if s is not None:
            scene = s.name
        else:
            scene = 'Unknown'
        logger.info(self, "Spawned in {scene}, at position {pos}".format(scene=scene, pos=evt.get("position", 'Unknown')))
        
                    
