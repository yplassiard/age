# *-* coding: utf8 *-*
import time

import pygame
import constants
import core
from pygame.locals import *

import gameconfig
import speech
import logger
import audio
import eventManager
import objectManager
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
	if objectManager.initialize() is False:
		logger.error("main", "Failed to initialize object manager.")
		return
	
	pygame.init()
	vi = pygame.display.Info()
	screen = pygame.display.set_mode((vi.current_w, vi.current_h), pygame.FULLSCREEN)
	pygame.display.set_caption("A3 Game Engine 1.0")
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
	now = time.time()
	oldTime = now
	
	if sceneManager.loadScene(gameconfig.getStartScene()) is False:
		print("Failed to load first scene {name}".format(name=gameconfig.getStartScene()))
		return
	stopAnimation()
	while 1:
		event = pygame.event.poll()
		if event.type == QUIT:
			break
		elif event.type == pygame.KEYDOWN and isInAnimation() is False:
			sceneManager.onKeyDown(event)
		elif event.type == pygame.KEYUP and isInAnimation() is False:
			sceneManager.onKeyUp(event)
		# check our own events

		eventManager.pump()
		
		now = time.time()
		# logger.info('main', "Tick is {time}".format(time=now))
		if now - oldTime > constants.INTERVAL_TICK_RESOLUTION:
			currentTicks = pygame.time.get_ticks()
			eventManager.post(eventManager.SCENE_INTERVAL_TICK, {"time": currentTicks})
			oldTime = now
	logger.log("main", "Exiting game.")
	pygame.quit()
