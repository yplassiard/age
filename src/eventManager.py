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
# hero specific events
HERO_SPAWN = 50
HERO_WALK = 51
HERO_RUN = 52



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
    QUIT_GAME: "quit_game",
    PAUSE_GAME: "pause_game",

    HERO_SPAWN: "hero_spawn",
    HERO_WALK: "hero_walk",
    HERO_RUN: "hero_run"
}

def addListener(obj):
    """Adds obj as a listener who will be notified when events occur, if the corresponding method
is found within obj's implementation."""
    global eventListeners

    if obj is not None:
        eventListeners.append(obj)

def post(type, data=None, target=None):
    """Posts an event to all listeners. the type argument must be one of the defined eventManager
constants above. The data argument is a dict which may contain any useful data for listeners.
"""
    if isinstance(type, int) is False:
        raise RuntimeError("Event type parameter has to be integer.")
    global eventQueue
    
    eventQueue.put({"type": type, "data": data, "target": target})


def dispatch(event):
    """Dispatches incoming event to listeners that implement the appropriate method."""
    global eventNames
    global eventListeners

    script = "event_%s" % eventNames.get(event.get("type", 'unknown'), None)
    target = event.get("target", None)
    targets = []
    if target is not None:
        target.append(target)
    else:
        targets.extend(eventListeners)
    for listener in targets:
        method = getattr(listener, script, None)
        if method:
            try:
                method(event.get('data', None))
            except Exception as e:
                logger.error("eventManager", "Failed to execute {name}.{script}({event}): {exception}".format(name=listener.__class__.__name__, script=script, event=event, exception=e))
                continue
