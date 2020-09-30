# *-* config: utf8 *-*

import scene
import scene_manager

class Scene(scene.MenuScene):
    name = 'userOptions'
    title = "Options"


    def __init__(self, name, config):
        super().__init__(name, {
            "select-sound": "menuSelect",
            "validate-sound": "menuValidate",
            "cancel-sound": "menuCancel",
            "choices": []
        })
        
    
    def activate(self, silent, params=None):
        idx = 0
        parent = params.get("__parent", "__quit")
        self.choices = ["Retour", ["Voix"]]
        import speech
        self.tts = speech.getInstance()
        if self.tts.hasVoiceSelectionSupport():
            self.voices = self.tts.listVoices()
            for voice in self.voices:
                self.choices[1].append(voice["name"])
        
        self.links = {str(0): parent.name}
        super().activate(silent, params)

    def event_menu_option_changed(self, evt):
        idx = evt.get("optionIndex", None)
        if idx != None:
            voice = self.voices[idx - 1]
            if voice is not None:
                self.tts.selectVoice(voice)
                
