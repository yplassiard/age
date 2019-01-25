# *-* coding: utf8 *-*

from objects import *
import math

objectsMap = {
    "key": Key,
    "chest": Chest,
    "npc": NonPlayableCharacter,
    "enemy": Enemy
}

_instance = None

class ObjectManager(object):
    """Manages all in-game objects."""
    objects = {}
    totalObjects = 0
    loadedObjects = 0

    def __init__(self):
        pass

    def load(self, config):
        """Loads all defined objects within the given configuration."""
        name = gameconfig.getValue(config, "name", str)
        if name is None:
            logger.error(self, "Each object has to be named with a \"name\" property")
            return False
        if self.objects.get(name, None) is not None:
            logger.error(self, "The object's name \"{name}\" is already defined".format(name=name))
            return False
        type = gameconfig.getValue(config, "type", str)
        cls = objectsMap.get(type, None)
        if cls is None:
            logger.error(self, "{name}'s type {type} is not known".format(name=name, type=type))
            return False
        try:
            o = cls(name, config)
        except Exception as e:
            logger.error(self, "Error instanciating {cls}({name}): {exception}".format(cls=cls.__name__, name=name, exception=e))
            return False
        self.objects[name] = o
        return o

    def get(self, name):
        o = self.objects.get(name, None)
        if o is None:
            logger.warning(self, "Object {name} is not known".format(name=name))
        return o

    def getLogName(self):
        return 'ObjectManager'

    def getNearestObject(self, position, direction, player, objectsList):
        lastDistance = None
        nearest = None
        if len(objectsList) == 0:
            objectsList = self.objects
        for value in objectsList:
            obj = self.objects[value] if isinstance(value, str) else value
            distance = math.sqrt(((obj.position[0] - position[0]) * (obj.position[0] - position[0]))\
                                 + ((obj.position[1] - position[1]) * (obj.position[1] - position[1])))
            
            if lastDistance is None:
                lastDistance = distance
                nearest = obj
                continue
            if lastDistance is not None and abs(lastDistance) > abs(distance):
                lastDistance = distance
                nearest = obj
        return (nearest, distance)
    
def initialize():
    global _instance

    if _instance is None:
        try:
            om = ObjectManager()
            _instance = om
        except Exception as e:
            logger.error("ObjectManager", "Failed to initialize object manager: {e}".format(e=e))
            return False
    return True

def addObject(config):
    global _instance

    if _instance is not None:
        return _instance.load(config)
    else:
        return False
    

def getObject(name):
    global _instance

    if _instance is not None:
        return _instance.get(name)
    else:
        return None
    
def getNearestObject(position, direction, player, objectsList=[]):
    global _instance

    if _instance is not None:
        return _instance.getNearestObject(position, direction, player, objectsList)
    return (None,None)
