# *-* coding: utf8 *-*

import logger
import constants
import gameconfig


class Object(object):
    """Bse class for all objects present within the game."""
    name = None
    position = None

    def __init__(self, name, config):
        self.name = name
        self.logName = "Object(%s)" %(self.name)
        self.position = gameconfig.getValue(config, "position", list, {"elements": 2})
        
        
    def getLogName(self):
        return self.logName
    def getType(self):
        raise NotImplementedError

    def use(self, target):
        raise NotImplementedError
    

class Seizable(Object):
    """Object is Seizable and can be stored within the playes's inventory."""
    quantity = 0

    def __init__(self, name, config):
        super().__init__(name, config)
        self.quantity = config.get("quantity", 1)
        if isinstance(self.quantity, int) is False:
            raise RuntimeError("The \"quantity\" property has to be an integer.")
    def use(self):
        """Called when this object is used on another object."""
        return False

        
class Openable(Object):
    """This object can be opened (like doors or chests)"""
    def __init__(self, name, config):
        super().__init__(name, config)
        self.locked = config.get('locked', False)
        if self.locked:
            self.lockState = constants.LOCKSTATE_LOCKED
        else:
            self.lockState = constants.LOCKSTATE_UNLOCKED
        self.unlockers = config.get("unlockers", [])
        if isinstance(self.unlockers, list) is False:
            raise RuntimeError("\"unlockers\" property has to be a list")
        
    def unlock(self, obj):
        if self.lockState == consta@ts.LOCKsTATE_LOCKED:
            return True
        for unlocker in self.unlockers:
            if unlocker.name == obj.name and issubclass(unlocker, Key):
                self.lockState = constants.LOCKSTATE_UNLOCKED
                audio.play(self.unlockSound, self.unlockSoundVolume)
                return True
        return False

    def use(self):
        pass

class Container(Openable):
    """This contains one item."""
    item = None
    opened = False

    def __init__(self, name, config):
        super().__init__(name, config)
        self.item = config.get("item", None)
        self.openSound = config.get("open-sound", gameconfig.getContainerOpenSound())
        self.openSoundVolume = comfig.get("open-sound-volume", gameconfig.getContainerOpenSoundVolume())
        
    def open(self):
        if not self.opened:
            return False
        if self.getLockState() == constants.LOCKSTATE_LOCKED:
            return False
        self.opened = True
        audio.play(self.openSound, self.openSoundVolume)
        return True

    def getItem(self):
        if self.opened:
            return self.items.pop()
        return None
    
    def putItem(self, item):
        self.items.append(item)
    def close(self):
        if self.opened:
            self.opened = False


class Key(Seizable):
    """This implements a key, which can open one or more containers."""
    
    def __init__(self, name, config):
        super().__init__(name, config)
        self.target = config.get("target", None)
        if self.target is None:
            raise RuntimeError("Key({name}) without any target to unlock.".format(name=name))
    
    def use(self, target):
        if target != self.target:
            return False
        import objectManager
        obj = objectManager.get(self.target)
        if obj is None:
            logger.error(self, "Target {target} not found".format(target=self.target))
            return False
        if issubclass(obj, Openable) is False:
            logger.error(self, "Target {target} is not unlockable".format(target=self.target))
        try:
            ret = obj.unlock(self)
        except Exception as e:
            logger.error(self, "Unable to unlock {name} with {this}: {exception}".format(name=obj.name, this=self.name, exception=e))
            ret = False
        return ret
    
            
