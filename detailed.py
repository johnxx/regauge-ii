import gauge_face

class Detailed(gauge_face.GaugeFace):
    def __init__(self, name, options, resources):
        super().__init__(name, options, resources)

    def config_updated(self, message):
        pass
    
    def update(self):
        pass