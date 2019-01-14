# *-* coding: utf8 *-*

from objects import *

objectsMap = {
    "key": Key
}

_instance = None

class ObjectManager(self):
    """Manages all in-game objects."""
    objects = {}
    totalObjects = 0
    loadedObjects = 0

    def __init__(self, config):
        ret = self.load(config)
        if ret is False:
            raise RuntimeError(self, "Objects failed to load")

    def load(self, config):
        """Loads all defined objects within the given configuration."""
        objs = config.get("object", [])
        if isinstance(objs, list) is False:
            logger.error(self, "The \"objects\" property has to be a list")
            return False
        for obj in objs:
            totalObjects += 1
            name = obj.get("name", None)
            if name is None:
                logger.error(self, "Each object has to be named with a \"name\" property")
                continue
            if self.objects.get(name, None) is not None:
                logger.error(self, "The object's name \"{name}\" is already defined".format(name=name))
                continue
            type = obj.get("type", None)
            cls = objectsMap.get(type, None)
            if cls is None:
                logger.error(self, "{name}'s type {type} is not known".format(name=name, type=type))
                continue
            try:
                o = cls(name, obj)
            except Exception as e:
                logger.error(self, "Error instanciating {cls}({name}): {exception}".format(cls=cls.__name__, name=name, exception=e))
                continue
            self.loadedObjects += 1
        if self.totalObjects > self.loadedObjects:
            print("{count} objects failed to load. Examine the log file to know more about this.".format(count=self.totalObjects - self.loadedObjects))
            return False
        return True

    def get(self, name):
        o = self.objects.get(name, None)
        if o is None:
            logger.warning(self, "Object {name} is not known".format(name=name))
        return o

    def getLogName(self):
        return 'ObjectManager'

def initialize(config):
    global _instance

    if _instance is None:
        try:
            om = ObjectManager(config)
            _instance = om
        except Exception as e:
            logger.error("ObjectManager", "Failed to initialize object manager.")
            return False
    return True

def addObject(config):
    global _instance

    if _instance is not None:
        return _instance.load(config)
    return False

