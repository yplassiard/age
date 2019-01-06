# *-* coding: utf-8 *-*

import pygame
from pygame.locals import *

import gameconfig
import speech
import logger
import audio


def main():
    logger.initialize()
    if speech.initialize() is False:
        logger.error("main", "Failed to start due to a lack of speech support.")
        return False
    speech.speak("Welcome to A2 Engine!")
    gc = gameconfig.GameConfig("a2engine.json")
    audioManager = audio.initialize(gc)
    
    pygame.init()
    vi = pygame.display.Info()
    screen = pygame.display.set_mode((vi.current_w, vi.current_h))
    pygame.display.set_caption("AA Engine 1.0")
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))
    font = pygame.font.Font(None, 36)
    text = font.render('A2 Engine', 1, (250, 250, 250))
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.centery = background.get_rect().centery
    background.blit(text, textpos)
    screen.blit(background, (0, 0))
    pygame.display.flip()

    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            screen.blit(background, (0, 0))
            pygame.display.flip()

if __name__ == '__main__':
    main()
