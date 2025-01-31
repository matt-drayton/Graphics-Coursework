class Material:
    def __init__(self, name=None, Ka=[1.,1.,1.], Kd=[1.,1.,1.], Ks=[1.,1.,1.], Ns=10.0):
        self.name = name
        self.Ka = Ka
        self.Kd = Kd
        self.Ks = Ks
        self.Ns = Ns


class MaterialLibrary:
    def __init__(self):
        self.materials = []
        self.names = {}

    def add_material(self,material):
        self.names[material.name] = len(self.materials)
        self.materials.append(material)

