# *-* codinhg: utf8 *-*

import sceneManager

class Scene(sceneManager.Scene):
    def __init__(self, name, config):
        super(Scene, self).__init__(name, config)
        if config is not None:
            self.choices = config.get(choices, [])
