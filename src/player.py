# *-* coding: utf8 *-*

import constants
import core
import gameconfig
import logger
import eventManager
from objects import Object

class Player(Object):
	"""Representing the main player."""
	health = None
	stamina = None
	staminaTicks = 0
	magic = None
	maxDistance = None
	maxStamina = None
	maxMagic = None
	maxHealth = None
	direction = constants.DIRECTION_NORTH

	def __init__(self, name, config):
		super().__init__(name, config)
		eventManager.addListener(self)
		self.maxHealth = gameconfig.getValue(config, "health", int, {"minValue": 1})
		self.maxMagic = gameconfig.getValue(config, "magic", int, {})
		self.maxStamina = gameconfig.getValue(config, "stamina", int, {"minValue": 1})
		self.maxDistance = gameconfig.getValue(config, "max-distance", float, {"defaultValue": 5})
		self.halth = self.maxHealth
		self.magic = 0
		self.staminaRecoveryTime = gameconfig.getValue(config, "stamina-recovery-time", int, {"defaultValue": constants.CHARACTER_STAMINA_RECOVERY_TIME})
		self.staminaDecrement = gameconfig.getValue(config, "stamina-decrement", int, {"defaultValue": 1})
		self.staminaIncrement = gameconfig.getValue(config, "stamina-increment", int, {"defaultValue": 1})
		self.stamina = self.maxStamina
		self.distance = self.maxDistance
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
	def handlePlayerMovements(self):
		if self.walking:
			if core.currentTicks - self.staminaDecrementTicks > self.staminaDecrementTime:
				self.stamina -= self.staminaDecrement
				self.staminaDecrementTicks = core.currentTicks
				eventManager.post(eventManager.CHARACTER_ATTRIBUTE_CHANGE, {"attribute": "stamina",
																															 "type": "decrease",
																															 "value": self.stamina})
			if self.stamina > 0 and core.currentTicks - self.walkingTicks > self.heroWalkTime:
				eventManager.post(eventManager.SCENE_MOVE, {"obj": self})
			elif self.stamina <= 0:
				logger.info(self, "Too tired to walk")
				self.stamina = 0
				self.walking = False
		elif self.running:
			if core.currentTicks - self.staminaDecrementTicks > self.staminaDecrementRunTime:
				self.stamina -= self.staminaDecrement
				self.staminaDecrementTicks = core.currentTicks
				eventManager.post(eventManager.HERO_ATTRIBUTE_CHANGE, {"attribute": "stamina",
																															 "type": "decrease",
																															 "value": self.stamina})
			if self.stamina > 0 and core.currentTicks - self.runningTicks > self.heroRunTime:
				eventManager.post(eventManager.SCENE_MOVE, {"obj": self})
			elif self.stamina <= 0:
				logger.info(self, "Too tired to run")
				self.stamina = 0
				self.walking = False
				
				


	def event_will_character_move(self, evt):
		if self.stamina > 0:
			self.direction = evt["direction"]
			running = evt.get("type", "walk")
			if running == "walk":
				self.walking = True
				self.running = False
			elif running == "run":
				self.walking = False
				self.running = True
		else:
			eventManager.post(eventManager.CHARACTER_TIRED, {"obj": self})
			return False
		return True
	def event_character_move(self, evt):
		pass # nothing to do here.
	def event_did_character_move(self, evt):
		self.stamina -= self.staminaDecrement
		
		 
	def event_character_spawn(self, evt):
		s = evt.get("scene", None)
		if s is not None:
			scene = s.name
		else:
			scene = 'Unknown'
		logger.info(self, "Spawned in {scene}, at position {pos}".format(scene=scene, pos=evt.get("position", 'Unknown')))
				
										

	def event_scene_interval_tick(self, evt):
		if self.stamina == self.maxStamina:
			return True
		delta = core.currentTicks - self.staminaTicks
		if delta > self.staminaRecoveryTime:
			self.stamina += self.staminaIncrement
			logger.info(self, "Recovering stamina {s}%, delta+{delta}".format(s=(self.stamina / self.maxStamina * 100), delta=delta))
			self.staminaTicks = core.currentTicks
		if self.stamina >= self.maxStamina:
			logger.info(self, "Stamina recovered")
			self.stamina = self.maxStamina

	
	def event_walk_start(self, evt):
		self.walking = False
		self.running = False
		if self.stamina > 0:
			self.walking = True
	def event_walk_stop(self, evt):
		self.walking = False
		self.running = False
	def event_run_start(self, evt):
		self.walking = False
		self.running = False
		if self.stamina > 0:
			self.running = True
	def event_run_stop(self, evt):
		self.walking = False
		self.running = False
		
