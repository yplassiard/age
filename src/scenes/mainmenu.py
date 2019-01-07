# *-* codinhg: utf8 *-*

import sceneManager
import logger



class Scene(sceneManager.MenuScene):
    def __init__(self, name, config):
        self.title = 'Main Menu'
        super().__init__(name, {"choices": ['New game', 'Continue', 'Exit'],
                                     "speak-title": True})
        
                                    

