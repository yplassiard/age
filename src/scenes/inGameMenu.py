# *-* config: utf8 *-*

import scene
import scene_manager

class Scene(scene.MenuScene):
    name = 'inGameMenu'
    title = "Pause"


    def __init__(self, name, config):
        super().__init__(name, {
            "select-sound": "menuSelect",
            "validate-sound": "menuValidate",
            "cancel-sound": "menuCancel",
            "choices": []
        })
        
    
    def activate(self, silent=False, params=None):
        idx = 0
        self.choices = ["Retour", "Options", "Quitter"]
        self.links = {str(0): "__unstack",
                      str(1): "userOptions",
                      str(2): "__quit"}
        
        super().activate(silent, params)
    
