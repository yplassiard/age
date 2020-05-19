# *-* coding: utf8 *-*

import logger
import constants
import gameconfig
import eventManager

class Object(object):
	"""Base class for all objects present within the game."""
	name = None
	position = None
	signalSound = None
	interactDistance = -1
	size = (1, 1)
	

	def __init__(self, name, config):
		self.name = name
		self.logName = "Object(%s)" %(self.name)
		eventManager.addListener(self)
		self.position = gameconfig.getValue(config, "position", list, {"elements": 2})
		self.size = gameconfig.getValue(config, "size", list, {"elements": 2})
		self.signalSound = "signal-sound"
		self.interactDistance = gameconfig.getValue(config, "interact-distance", float, {"defaultValue": -1})
		
				

	def getInteractionDistance(self):
		"""Automatically interact with this object if the distance is below this value"""
		return self.interactDistance
				
				
	def getLogName(self):
		return "%s(%s)" %(self.__class__.__name__, self.name)
	def __repr__(self):
		return self.getLogName()
		
	def getType(self):
		raise NotImplementedError

	def getPosition(self):
		return self.position

	def getSize(self):
		return self.size
	
	def getSignalSound(self):
		return self.signalSound
		
	def use(self, target):
		raise NotImplementedError
		

class Seizable(Object):
	"""Object is Seizable and can be stored within the playes's inventory."""
	quantity = 0
	
	def __init__(self, name, config):
		super().__init__(name, config)
		self.quantity = gameconfig.getValue(config, "quantity", int, {"defaultValue": 1,
																																			"minValue": 1})
				
	def use(self, target):
		"""Called when this object is used on another object."""
		return False

				
class Openable(Object):
	"""This object can be opened (like doors or chests)"""
	def __init__(self, name, config):
		super().__init__(name, config)
		self.locked = gameconfig.getValue(config, 'locked', bool, {"defaultValue": False})
		if self.locked:
			self.lockState = constants.LOCKSTATE_LOCKED
		else:
			self.lockState = constants.LOCKSTATE_UNLOCKED
		self.unlockers = gameconfig.getValue(config, "unlockers", list, {"defaultValue": [],
																																		 "elements": 0})

				
	def unlock(self, obj):
		if self.lockState == consta@ts.LOCKsTATE_UNLOCKED:
			return True
		for unlockerStr in self.unlockers:
			import objectManager
			
			unlocker = objectManager.getObject(unlockerStr)
			if unlocker is not None and unlocker.name == obj.name and issubclass(unlocker, Key):
				self.lockState = constants.LOCKSTATE_UNLOCKED
				eventManager.post(eventManager.OBJECT_UNLOCK, {"container": self,
																											 "unlocker": unlocker})
				audio.play(self.unlockSound, self.unlockSoundVolume)
				return True
		return False



class Chest(Openable):
	"""This contains one item."""
	item = None
	opened = False
	
	def __init__(self, name, config):
		super().__init__(name, config)
		self.item = gameconfig.get(config, "item", str, {"defaultValue": None})
		self.openSound = config.get("open-sound", gameconfig.getContainerOpenSound())
		self.openSoundVolume = config.get("open-sound-volume", gameconfig.getContainerOpenSoundVolume())
		self.signalSound = "chest-signal-sound"
		
	def open(self):
		if self.opened:
			return True
		if self.getLockState() == constants.LOCKSTATE_LOCKED:
			return False
		self.opened = True
		audio.play(self.openSound, self.openSoundVolume)
		return True

	def getItem(self):
		if self.opened:
			i = self.item
			self.item = None
			return i
		return None
	
	def putItem(self, item):
		if self.item is not None:
			return False
		self.item = item
		
	def close(self):
		if self.opened:
			self.opened = False


class Key(Seizable):
	"""This implements a key, which can open one or more containers."""
	
	def __init__(self, name, config):
		super().__init__(name, config)
		self.target = gameconfig.getValue(config, "target", str, {"defaultValue": None})
		if self.target is None:
			raise RuntimeError("Key({name}) without any target to unlock.".format(name=name))
		self.signalSound = "key-signal-sound"
		
	def use(self, target):
		if target != self.target:
			return False
		import objectManager
		obj = objectManager.getObject(self.target)
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
		
						

class NonPlayableCharacter(Object):
	"""This is a non-playable character. It will instanciate a StoryText scene when talking to him,
i.e when using this object."""
	storyScene = None
	autoInteract = None
	interactCount = 0

	def __init__(self, name, config):
		super().__init__(name, config)
		self.size = (1,1)
		scene = gameconfig.getValue(config, "scene", str, {"defaultValue": None})
		interact = gameconfig.getValue(config, "auto-interact", str, {"defaultValue": 'never'})
		if interact not in ["never", "once", "always"]:
			raise RuntimeError("auto-interact value {v} should be one of 'never', 'once', 'always'".format(v=interact))
		self.autoInteract = interact
		if scene is None:
			raise RuntimeError("No story scene configured for this NPC.")
		import sceneManager
		if sceneManager.sceneExists(scene) is False:
			logger.error(self, "{scene} not found.".format(scene=scene))
			raise RuntimeError("Invalid NPC configuration: Scene not found")
		self.storyScene = scene
		self.signalSound = gameconfig.getValue(config, "signal-sound", str)
		self.hitMax = gameconfig.getValue(config, "hit-count", int, {"defaultValue": -1})
		self.hitCount = 0
		self.hitScene = gameconfig.getValue(config, "hit-scene", str, {"defaultValue": None})
		self.hitSound = gameconfig.getValue(config, "hit-sound", str)
		self.interactDistance = 0
		

	def onInteract(self, scene, player, onPurpose=False):
		if (self.autoInteract == 'once' and self.interactCount == 0) or self.autoInteract == 'always' or onPurpose:
			self.use(None)
			self.interactCount += 1
			return True
		return False

	def event_object_hit(self, evt):
		obj = evt.get("obj", None)
		if obj != self:
			return True
		self.hitCount += 1

	def event_did_object_hit(self, evt):
		if self.hitMax != -1 and self.hitCount == self.hitMax:
			self.hitCount = 0
			import sceneManager

			if sceneManager.sceneExists(self.hitScene) is False:
				logger.error(self, "{scene} does not exist".format(scene=self.hitScene))
				return False
			sceneManager.stackScene(self.hitScene)
		return True
	
	def use(self, target):
		if self.storyScene is not None:
			import sceneManager
			sceneManager.stackScene(self.storyScene)

						
class Enemy(Object):
	"""Defines an opponent that can move and attack the player."""
	health = 100
	
	def __init__(self, name, config):
		super().__init__(name, config)
		self.health = gameconfig.getValue(config, "health", int, {"minValue": 1,
																															"defaultValue": constants.ENEMY_DEFAULT_HEALTH})
		self.signalSound = "enemy-signal-sound"
		

