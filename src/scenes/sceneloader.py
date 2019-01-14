# *-* config: utf8 *-*

import scene
import sceneManager

class Scene(scene.MenuScene):
    name = 'sceneloader'
    title = 'Choose a scene to load'


        
    def activate(self, silent, params=None):
        idx = 0
        for name in sceneManager._instance.scenes:
            self.links[str(idx)] = name
            self.choices.append(name)
            idx += 1
        super().activate(silent)
        

    def input_press_action(self):
        sceneManager.leaveCurrentScene()
