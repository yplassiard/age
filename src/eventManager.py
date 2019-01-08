# *-* coding utf8 *-*

import pygame

import logger

# general game events

INITÆGAME = 1
QUIT_GAME = 2
PAUSE_GAME = 3

# scene events
LOAD_SCENE = 10
LEAVE_SCENE = 11


# List objects receiving custom game events.
eventListeners = []

# Maps event constants to strings to ease event handler executions.
eventNames = {
    LOAD_SCENE: "load_scene",
    LEAVE_SCENE: "leave_scene",
    QUIT_GAME: "quit_game",
    PAUSE_GAME: "pause_game"
}

def addListener(obj):
    """Adds obj as a listener who will be notified when events occur, if the corresponding method
is found within obj's implementation."""
    global eventListeners

    if obj is not None:
        eventListeners.append(obj)

def post(type, data=None):
    """Posts an event to all listeners. the type argument must be one of the defined eventManager
constants above. The data argument is a dict which may contain any useful data for listeners.
"""
    if isinstance(type, int) is False:
        raise RuntimeError("Event type parameter has to be integer.")
    
    pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"type": type, "data": data}))


def dispatch(event):
    """Dispatches incoming event to listeners that implement the appropriate method."""
    global eventNames
    global eventListeners

    script = "event_%s" % eventNames.get(event.dict.get("type", 'unknown'), None)
    for listener in eventListeners:
        method = getattr(listener, script, None)
        if method:
            try:
                method(event.dict)
            except Exception as e:
                logger.error("eventManager", "Failed to execute {name}.{script}: {exception}".format(name=listener.__class__.__name__, sccript=script, exception=e))
                continue
