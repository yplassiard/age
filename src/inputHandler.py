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
	pygame.K_SPACE: "pause",
	pygame.K_TAB: "tab"
}

lastKeyPressed = None

def action(event):
		"""Maps the given keyboard event (or joystick) to an action.)."""

		global keyboardMap
		global lastKeyPressed
		
		ret = keyboardMap.get(event.key, pygame.key.name(event.key))
		if ret is not None:
				if event.mod & pygame.KMOD_SHIFT:
						ret = "shift_%s" % ret
				if event.mod & pygame.KMOD_CTRL:
						ret = "control_%s" % ret
				if event.mod & pygame.KMOD_ALT:
						ret = "alt_%s" % ret
				if event.mod & pygame.KMOD_META:
						ret = "windows_%s" % ret
				lastKeyPressed = ret if event.type == pygame.KEYDOWN else None
				return ret
		return None


def getLastKeyPressed():
		global lastKeyPressed

		return lastKeyPressed
