# *-* coding: utf8 *-*

# Defines main game constants that can be used everywhere

# global configuration
CONFIG_RESOURCE_DIR = "res"
CONFIG_DATA_DIR = "data"
INTERVAL_TICK_RESOLUTION = 1

# Audio constants
AUDIO_FX_VOLUME = 0.8
AUDIO_FX_SIGNAL_VOLUME = (AUDIO_FX_VOLUME / 1.5)
AUDIO_MUSIC_VOLUME = 0.8
AUDIO_ERROR_SOUND = "error-sound"
AUDIO_MESSAGE_SOUND = "message"
AUDIO_MESSAGE_FINISH_SOUND = "messageFinished"

AUDIO_FOOTSTEP_WALK_SOUND = "walk"
AUDIO_FOOTSTEP_RUN_SOUND = "run"

# Scene constants

SCENE_MININUM_INTERVAL = 10 # milliseconds
# directions the player can go to

DIRECTION_NORTH = 0
DIRECTION_SOUTH = 1
DIRECTION_EAST = 2
DIRECTION_WEST = 3


# Objects specific constants
HERO_WALK_TIME = 500
HERO_RUN_TIME = 300

# Peckables
LOCKSTATE_LOCKED = 100
LOCKSTATE_UNLOCKED = 101
