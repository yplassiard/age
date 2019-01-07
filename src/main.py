# *-* coding: utf-8 *-*

import pygame
from pygame.locals import *

import gameconfig
import speech
import logger
import audio
import sceneManager


def main():
    logger.initialize()
    if speech.initialize() is False:
        logger.error("main", "Failed to start due to a lack of speech support.")
        return False
    speech.cancelSpeech()
    speech.speak("Welcome to A3 Game Engine!")
    gc = gameconfig.GameConfig("a3g-engine.json")
    sceneManager.initialize(gc)
    audioManager = audio.initialize(gc)
    
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

    sceneManager.loadScene("mainmenu")
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                sceneManager.onKeyDown(event.key)
            elif event.type == pygame.KEYUP:
                sceneManager.onKeyUp(event.key)
            # screen.blit(background, (0, 0))
            # pygame.display.flip()

if __name__ == '__main__':
    main()
