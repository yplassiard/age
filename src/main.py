# *-* coding: utf-8 *-*

import pygame
from pygame.locals import *

import gameconfig
import speech
import logger
import audio
import eventManager
import sceneManager


def main():
    logger.initialize()
    if speech.initialize() is False:
        logger.error("main", "Failed to start due to a lack of speech support.")
        return False
    speech.cancelSpeech()
    speech.speak("Welcome to A3 Game Engine!")
    gc = gameconfig.GameConfig("a3g-engine.json")
    if gc is None:
        logger.error("main", "Invalid configuration.")
        return
    if sceneManager.initialize(gc) is False:
        logger.error("main", "Unable to initialize scenes.")
        return
    if audio.initialize(gc) is False:
        logger.error("main", "Failed to initialize sound support.")
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
    ticks = pygame.time.get_ticks()
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.VIDEOEXPOSE:
                sceneManager.loadScene("mainmenu")
            elif event.type == QUIT:
                return
            elif event.type == pygame.USEREVENT:
                eventManager.dispatch(event)
            elif event.type == pygame.KEYDOWN:
                sceneManager.onKeyDown(event.key, event.mod)
            elif event.type == pygame.KEYUP:
                sceneManager.onKeyUp(event.key, event.mod)
            # screen.blit(background, (0, 0))
            # pygame.display.flip()

        if pygame.time.get_ticks() - ticks == 0:
            pygame.time.wait(1)
        ticks = pygame.time.get_ticks()
    logger.log("main", "Exiting game.")
    
if __name__ == '__main__':
    main()
