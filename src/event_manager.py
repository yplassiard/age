# *-* coding utf8 *-*

import queue
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

# Menu Scene
MENU_OPTION_CHANGE = 20
MENU_SELECT = 21
MENU_ITEM_CHANGE = 22

# character specific events
CHARACTER_SPAWN = 50
CHARACTER_MOVE = 51
CHARACTER_ATTRIBUTE_CHANGE = 52
CHARACTER_HIT = 53
CHARACTER_TIRED = 54
CHARACTER_DIED = 55


# object specific events
OBJECT_TAKE = 70
OBJECT_DROP = 71
OBJECT_LOCK = 72
OBJECT_UNLOCK = 73
OBJECT_HIT = 74


# Audio specific events
AUDIO_RENDER = 100
AUDIO_PLAY_3D = 101
AUDIO_CAMERA_CHANGE = 102



# List objects receiving custom game events.
EVENT_LISTENERS = []
EVENT_QUEUE = queue.Queue()

def pump():
    global EVENT_QUEUE

    try:
        e = EVENT_QUEUE.get(block=False)
    except queue.Empty:
        return
    dispatch(e)

# Maps event constants to strings to ease event handler executions.
EVENT_NAMES = {
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


        MENU_OPTION_CHANGE: "menu_option_changed",
        MENU_ITEM_CHANGE: "menu_item_changed",
        MENU_SELECT: "menu_select",

    CHARACTER_SPAWN: "character_spawn",
    CHARACTER_MOVE: "character_move",
    CHARACTER_ATTRIBUTE_CHANGE: "character_attribute_change",
    CHARACTER_HIT: "character_hit",
    CHARACTER_TIRED: "character_tired",
    CHARACTER_DIED: "character_died",

    OBJECT_TAKE: "object_take",
    OBJECT_DROP: "object_drop",
    OBJECT_LOCK: "object_lock",
    OBJECT_UNLOCK: "object_unlock",
    OBJECT_HIT: "object_hit",

    AUDIO_RENDER: "audio_render",
    AUDIO_PLAY_3D: "audio_play_3d",
    AUDIO_CAMERA_CHANGE: "audio_camera_change",

}

def add_listener(obj):
    """Adds obj as a listener who will be notified when events occur, if the corresponding method
is found within obj's implementation."""
    global EVENT_LISTENERS

    if obj is not None:
        logger.debug("event_manager", "addListener({name})".format(name=getattr(obj, "name", obj.__class__.__name__)))
        EVENT_LISTENERS.append(obj)

def remove_listener(obj):
    """Removes a registered object"""
    global EVENT_LISTENERS

    if obj is None:
        return
    EVENT_LISTENERS.remove(obj)

def post(type, data=None, target=None):
    """Posts an event to all listeners. the type argument must be one of the defined event_manager
constants above. The data argument is a dict which may contain any useful data for listeners.
"""
    if isinstance(type, int) is False:
        raise RuntimeError("Event type parameter has to be integer.")
    global EVENT_QUEUE
    global EVENT_NAMES

    EVENT_QUEUE.put({"type": type, "data": data, "target": None})
    if type not in [SCENE_INTERVAL_TICK]:
        logger.debug("event_manager", "Posted event {evt}".format(evt=EVENT_NAMES.get(type, "UNKNOWN")))

def dispatch(event):
    """Dispatches incoming event to listeners that implement the appropriate method."""
    global EVENT_NAMES
    global EVENT_LISTENERS
    
    script = "event_%s" % EVENT_NAMES.get(event.get("type", 'unknown'), None)
    will_script = "event_will_%s" % EVENT_NAMES.get(event.get("type", 'unknown'), None)
    did_script = "event_did_%s" % EVENT_NAMES.get(event.get("type", 'unknown'), None)
    target = event.get("target", None)
    targets = []
    if target is not None:
        target.append(target)
    else:
        targets.extend(EVENT_LISTENERS)
    will_chain = []
    do_chain = []
    did_chain = []
    for listener in targets:
        method = getattr(listener, script, None)
        will_method = getattr(listener, will_script, None)
        did_method = getattr(listener, did_script, None)
        if will_method:
            will_chain.append((will_method, listener))
        if method:
            do_chain.append((method, listener))
        if did_method:
            did_chain.append((did_method, listener))
    for list in [will_chain, do_chain, did_chain]:
        for method, listener in list:
            ret = logger.debug("event_manager", "{obj}.{script}".format(obj=listener.__class__.__name__, script=method.__name__)) if not "interval" in method.__name__ else None
            try:
                ret = method(event.get('data', None))
            except Exception as e:
                logger.exception("event_manager", "Failed to execute {name}.{script}({event}): {exception}".format(name=listener.__class__.__name__, script=method.__name__, event=event, exception=e), e)
                ret = False
            if ret is False:
                logger.debug("event_manager", "{obj}.{script}: blocked event propagation".format(obj=listener.__class__.__name__, script=method.__name__))
                return
