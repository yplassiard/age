# *-* coding utf8 *-*

import queue
import pygame

import logger

# general game events

INITÆGAME = 1
QUIT_GAME = 2
PAUSE_GAME = 3

# scene events
LOAD_SCENE = 10
LEAVE_SCENE = 11
LEAVE_CURRENT_SCENE = 12
SCENE_INTERVAL_ACTIVATE = 13
SCENE_INTERVAL_DEACTIVATE = 14
SCENE_INTERVAL_TICK = 15
SCENE_STACK = 16
SCENE_UNSTACK = 17

# character specific events
CHARACTER_SPAWN = 50
CHARACTER_MOVE = 51
CHARACTER_ATTRIBUTE_CHANGE = 52
CHARACTER_HIT = 53
CHARACTER_TIRED = 54
CHARACTER_DIED = 55




# List objects receiving custom game events.
eventListeners = []
eventQueue = queue.Queue()

def pump():
	global eventQueue
		
	try:
		e = eventQueue.get(block=False)
	except queue.Empty:
		return
	dispatch(e)

# Maps event constants to strings to ease event handler executions.
eventNames = {
	LOAD_SCENE: "load_scene",
	LEAVE_SCENE: "leave_scene",
	LEAVE_CURRENT_SCENE: "leave_current_scene",
	SCENE_INTERVAL_ACTIVATE: "scene_interval_activate",
	SCENE_INTERVAL_DEACTIVATE: "scene_interval_deactivate",
	SCENE_INTERVAL_TICK: "scene_interval_tick",
	SCENE_STACK: "scene_stack",
	SCENE_UNSTACK: "scene_unstack",
	QUIT_GAME: "quit_game",
	PAUSE_GAME: "pause_game",
	
	CHARACTER_SPAWN: "character_spawn",
	CHARACTER_MOVE: "character_move",
	CHARACTER_ATTRIBUTE_CHANGE: "character_attribute_change",
	CHARACTER_HIT: "character_hit",
	CHARACTER_TIRED: "character_tired",
	CHARACTER_DIED: "character_died",
}

def addListener(obj):
	"""Adds obj as a listener who will be notified when events occur, if the corresponding method
is found within obj's implementation."""
	global eventListeners

	if obj is not None:
		logger.debug("eventManager", "addListener({name})".format(name=getattr(obj, "name", obj.__class__.__name__)))
		eventListeners.append(obj)
def removeListener(obj):
	"""Removes a registered object"""
	global eventListeners

	if obj is None:
		return
	eventListeners.remove(obj)

def post(type, data=None, target=None):
	"""Posts an event to all listeners. the type argument must be one of the defined eventManager
constants above. The data argument is a dict which may contain any useful data for listeners.
"""
	if isinstance(type, int) is False:
		raise RuntimeError("Event type parameter has to be integer.")
	global eventQueue
	global eventNames
	
	eventQueue.put({"type": type, "data": data, "target": None})
	logger.debug("eventManager", "Posted event {evt}".format(evt=eventNames.get(type, "UNKNOWN"))) if type not in [SCENE_INTERVAL_TICK] else None
		

def dispatch(event):
	"""Dispatches incoming event to listeners that implement the appropriate method."""
	global eventNames
	global eventListeners
	
	script = "event_%s" % eventNames.get(event.get("type", 'unknown'), None)
	willScript = "event_will_%s" % eventNames.get(event.get("type", 'unknown'), None)
	didScript = "event_did_%s" % eventNames.get(event.get("type", 'unknown'), None)
	target = event.get("target", None)
	targets = []
	if target is not None:
		target.append(target)
	else:
		targets.extend(eventListeners)
	willChain = []
	doChain = []
	didChain = []
	for listener in targets:
		method = getattr(listener, script, None)
		willMethod = getattr(listener, willScript, None)
		didMethod = getattr(listener, didScript, None)
		if willMethod:
			willChain.append((willMethod, listener))
		if method:
			doChain.append((method, listener))
		if didMethod:
			didChain.append((didMethod, listener))
	for list in [willChain, doChain, didChain]:
		for method, listener in list:
			logger.debug("eventManager", "{obj}.{script}".format(obj=listener.__class__.__name__, script=method.__name__)) if not "interval" in method.__name__ else None
			try:
				ret = method(event.get('data', None))
			except Exception as e:
				logger.exception("eventManager", "Failed to execute {name}.{script}({event}): {exception}".format(name=listener.__class__.__name__, script=method.__name__, event=event, exception=e), e)
				ret = False
			if ret is False:
				logger.debug("eventManager", "{obj}.{script}: blocked event propagation".format(obj=listener.__class__.__name__, script=method.__name__))
				return 
			
