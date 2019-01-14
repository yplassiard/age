# *-* coding: utf8 *-*

import constants
import gameconfig
import logger
import eventManager
from objects import Object

class Player(Object):
    haalth = None
    stamina = None
    magic = None

    def __init__(self, name, config):
        super().__init__(name, config)
        eventManager.addListener(self)
        self.health = gameconfig.getValue(config, "health", int, {"minValue": 1})
        self.magic = gameconfig.getValue(config, "magic", int, {})
        self.stamina = gameconfig.getValue(config, "stamina", int, {"minValue": 1})
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
    
    
                
                                            

    # events

    def event_hero_walk(self, evt):
        pass
    def event_hero_run(self, evt):
        pass
