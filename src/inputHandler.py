# *-* coding: utf8 *-*
import pygame

keyboardMap = {
    pygame.key.K_ESCAPE: "quit",
    pygame.key.K_ENTER: "action",
    pygame.key.K_UP: "up",
    pygame.key.K_DOWN: "down",
    pygame.key.K_LEFT: "left",
    pygame.key.K_RIGHT: "right",
    pygame.key.K_SPACE: "pause",
    pygame.key.K_Q: "firstButton",
    pygame.key.K_S: "secondButton"
}
def action(key):
    """Maps the given keyboard event (or joystick) to an action.)."""

    global keyboardMap
    
    for k in keyboardMap:
        ret = k.get(key, None)
        if ret is not None:
            return ret
    return None

