# *-* coding: utf8 *-*

import pygame
import constants
import core
from pygame.locals import *

import gameconfig
import speech
import logger
import audio
import eventManager
import sceneManager


currentTicks = 0

def startAnimation():
    global _inAnimation

    _inAnimation = True
def stopAnimation():
    global _inAnimation

    _inAnimation = False

def isInAnimation():
    global _inAnimation

    return _inAnimation

def main():
    global currentTicks, _inAnimation
    
    logger.initialize()
    if gameconfig.initialize("a3g-engine.json") is False:
        logger.error("main", "Invalid configuration.")
        return
    if speech.initialize() is False:
        logger.error("main", "Failed to start due to a lack of speech support.")
        return False
    speech.cancelSpeech()
    speech.speak("Chargement en cours...")
    startAnimation()

    if audio.initialize() is False:
        logger.error("main", "Failed to initialize sound support.")
        return
    if sceneManager.initialize() is False:
        logger.error("main", "Unable to initialize scenes.")
        print("Unable to initialize scenes: Check the logfile for more details.")
        return
    
    pygame.init()
    vi = pygame.display.Info()
    screen = pygame.display.set_mode((vi.current_w, vi.current_h))
    pygame.display.set_caption("AA Engine 1.0")
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))
    font = pygame.font.Font(None, 36)
    text = font.render('A3 Game Engine', 1, (250, 250, 250))
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.centery = background.get_rect().centery
    background.blit(text, textpos)
    screen.blit(background, (0, 0))
    pygame.display.flip()
    oldTime = 0
    clock = pygame.time.Clock()
    
    exposed = False
    while 1:
        event = pygame.event.poll()
        if event.type == pygame.VIDEOEXPOSE and exposed is False:
            if sceneManager.loadScene(gameconfig.getStartScene()) is False:
                print("Failed to load first scene {name}".format(name=gameconfig.getStartScene()))
                return
            else:
                exposed = True
                stopAnimation()
        elif event.type == QUIT:
            return
        elif event.type == pygame.KEYDOWN and isInAnimation() is False:
            sceneManager.onKeyDown(event.key, event.mod)
        elif event.type == pygame.KEYUP and isInAnimation() is False:
            sceneManager.onKeyUp(event.key, event.mod)
        # check our own events

        eventManager.pump()
        
        now = clock.tick(60)
        # logger.info('main', "Tick is {time}".format(time=now))
        if now > constants.INTERVAL_TICK_RESOLUTION:
            currentTicks = pygame.time.get_ticks()
            eventManager.post(eventManager.SCENE_INTERVAL_TICK, {"time": currentTicks})
            oldTime = now
    logger.log("main", "Exiting game.")
    pygame.quit()
