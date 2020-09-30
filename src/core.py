# *-* coding: utf8 *-*
""" AGE - Audio Game-Engine
Core module

Description: This modules contains the PyGame loop, responsible for managing input events (UI)
as well as the global game timer.
"""

import time

import pygame
from pygame.locals import *


import constants
import gameconfig
import speech
import logger
import audio
import event_manager
import objectManager
import scene_manager

_INSTANCE = None


class AGE():
    """Audio Game Engine base class"""

    current_ticks = 0
    in_animation = True

    def __init__(self):
        self.pygame_initialized = False


    def start_animation(self):
        """Enters a cut-scene."""

        self.in_animation = True

    def stop_animation(self):
        """Exits a cut-scene."""

        self.in_animation = False

    def is_in_animation(self):
        """
        Return whether a blocking animation (cut-scene) is running
        """
        return self.in_animation

    def init_pygame(self):
        """Initializes the Pygame engine."""
        pygame.init()
        myscreen = pygame.display.Info()
        screen = pygame.display.set_mode((myscreen.current_w, myscreen.current_h),
                                         pygame.FULLSCREEN)
        pygame.display.set_caption("Audio Game Engine 1.0")
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((0, 0, 0))
        font = pygame.font.Font(None, 36)
        text = font.render('Audio Game Engine', 1, (250, 250, 250))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery
        background.blit(text, textpos)
        screen.blit(background, (0, 0))
        pygame.display.flip()
        self.pygame_initialized = True


    def run(self):
        """
        The main method, where everything happens.
        """

        logger.initialize()
        if gameconfig.initialize("a3g-engine.json") is False:
            logger.error("main", "Invalid configuration.")
            return
        if speech.initialize() is False:
            logger.error("main", "Failed to start due to a lack of speech support.")
            return
        speech.cancelSpeech()
        speech.speak("Chargement en cours...")
        self.start_animation()

        if audio.initialize(gameconfig.get_global_audio_properties()) is False:
            logger.error("main", "Failed to initialize sound support.")
            return
        if scene_manager.initialize() is False:
            logger.error("main", "Unable to initialize scenes.")
            print("Unable to initialize scenes: Check the logfile for more details.")
            return
        if objectManager.initialize() is False:
            logger.error("main", "Failed to initialize object manager.")
            return
        self.init_pygame()
        now = time.time()
        old_time = now

        if scene_manager.load_scene(gameconfig.get_start_scene()) is False:
            print("Failed to load first scene {name}".format(name=gameconfig.getStartScene()))
            return
        self.stop_animation()
        while 1:
            event = pygame.event.poll()
            if event.type == QUIT:
                break
            if event.type == pygame.KEYDOWN and self.is_in_animation() is False:
                scene_manager.on_key_down(event)
            elif event.type == pygame.KEYUP and self.is_in_animation() is False:
                scene_manager.on_key_up(event)
            # check our own events

            event_manager.pump()

            now = time.time()
            # logger.info('main', "Tick is {time}".format(time=now))
            if now - old_time > constants.INTERVAL_TICK_RESOLUTION:
                self.current_ticks = pygame.time.get_ticks()
                event_manager.post(event_manager.SCENE_INTERVAL_TICK, {"time": self.current_ticks})
                old_time = now
        logger.info("main", "Exiting game.")
        speech.terminate()
        pygame.quit()

def initialize():
    global _INSTANCE

    _INSTANCE = AGE()

def run():
    global _INSTANCE

    _INSTANCE.run()

def start_animation():
    global _INSTANCE

    _INSTANCE.start_animation()
def stop_animation():
    global _INSTANCE

    _INSTANCE.stop_animation()
def is_in_animation():
    global _INSTANCE

    return _INSTANCE.is_in_animation()

def get_current_ticks():
    global _INSTANCE

    return _INSTANCE.current_ticks

