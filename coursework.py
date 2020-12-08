
# import the scene class
from scene import Scene

from blender import load_obj_file, Mesh

from BaseModel import *

from models2D import *

from FurModel import FurModel


class DrawModelFromMesh(BaseModel):
    '''
    Base class for all models, inherit from this to create new models
    '''

    def __init__(self, scene, M, mesh):
        '''
        Initialises the model data
        '''

        BaseModel.__init__(self, scene=scene, M=M),

        # load all data from the blender file
        #mesh = load_obj_file(file)

        # initialises the vertices of the shape
        self.vertices = mesh.vertices

        # initialises the faces of the shape
        #self.indices = mesh.faces[:,:,0]
        self.indices = mesh.faces

        if self.indices.shape[1] == 3:
            self.primitive = GL_TRIANGLES

        elif self.indices.shape[1] == 4:
            self.primitive = GL_QUADS

        else:
            print('(E) Error: Mesh should have 3 or 4 vertices per face!')

        # initialise the normals per vertex
        self.normals = mesh.normals

        # and save the material information
        self.material = Material(
            Ka=np.array([28/255, 18/255, 12/255], "f"),
            Kd=np.array([48/255, 32/255, 22/255], "f"),
            Ks=np.array([58/255, 38/255, 27/255], "f"),
            Ns=10.0,
        )

        # we force a bit of specularity to make it more visible
        self.material.Ns = 15.0

        # and we check which primitives we need to use for drawing
        if self.indices.shape[1] == 3:
            self.primitive = GL_TRIANGLES

        elif self.indices.shape[1] == 4:
            self.primitive = GL_QUADS

        else:
            print('(E) Error in DrawModelFromObjFile.__init__(): index array must have 3 (triangles) or 4 (quads) columns, found {}!'.format(
                self.indices.shape[1]))
            raise

        # default vertex colors to one (white)
        self.vertex_colors = np.ones((self.vertices.shape[0], 3), dtype='f')

        if self.normals is None:
            print('(W) No normal array was provided.')
            print('--> setting to zero.')
            self.normals = np.zeros(self.vertices.shape, dtype='f')

        # and bind the data to a vertex array
        self.bind()


if __name__ == '__main__':
    # initialises the scene object
    # scene = Scene(shaders='gouraud')
    scene = Scene()

    meshes = load_obj_file('models/bunny_world.obj')
    bunny = DrawModelFromMesh(scene=scene, M=poseMatrix(), mesh=meshes[0])

    scene.add_model(bunny)
    fur_model = FurModel(scene=scene, vertices=bunny.vertices, normals=bunny.normals,
                         indices=bunny.indices, M=poseMatrix(), material=bunny.material)

    scene.add_model(fur_model)

    # starts drawing the scene
    scene.run()
