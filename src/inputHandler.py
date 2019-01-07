# *-* coding: utf8 *-*
import pygame
import logger

keyboardMap = {
    pygame.K_ESCAPE: "quit",
    pygame.K_RETURN: "action",
    pygame.K_UP: "up",
    pygame.K_DOWN: "down",
    pygame.K_LEFT: "left",
    pygame.K_RIGHT: "right",
    pygame.K_SPACE: "pause"
}
def action(key, mods):
    """Maps the given keyboard event (or joystick) to an action.)."""

    global keyboardMap
    

    ret = keyboardMap.get(key, None)
    if ret is not None:
        if mods & pygame.KMOD_SHIFT:
            ret = "shift_%s" % ret
        if mods & pygame.KMOD_CTRL:
            ret = "control_%s" % ret
        if mods & pygame.KMOD_ALT:
            ret = "alt_%s" % ret
        if mods & pygame.KMOD_META:
            ret = "windows_%s" % ret
        return ret
    return None

