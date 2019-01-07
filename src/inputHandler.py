# *-* coding: utf8 *-*
import pygame

keyboardMap = {
    pygame.K_ESCAPE: "quit",
    pygame.K_RETURN: "action",
    pygame.K_UP: "up",
    pygame.K_DOWN: "down",
    pygame.K_LEFT: "left",
    pygame.K_RIGHT: "right",
    pygame.K_SPACE: "pause"
}
def action(key):
    """Maps the given keyboard event (or joystick) to an action.)."""

    global keyboardMap
    
    for k in keyboardMap:
        ret = k.get(key, None)
        if ret is not None:
            return ret
    return None

