# imports all openGL functions
from OpenGL.GL import *

# and we import a bunch of helper functions
from matutils import *

from material import Material
from BaseModel import BaseModel

class FurModel(BaseModel):
    '''
    Base class for all models, implementing the basic draw function for triangular meshes.
    Inherit from this to create new models.
    '''

    def __init__(self, scene, M=poseMatrix(), color=[1.,1.,1.], primitive=GL_TRIANGLES, visible=True):
        '''
        Initialises the model data
        '''

        self.fur_length = 0.1
        self.fur_angle = 0
        self.fur_density = 0
        self.fur_vertices = None

    def generate_fur_vertices(self):
        initial_fur = self.fur_length / 3
        secondary_fur = self.fur_length / (2/3)
        
        # Deep copy
        temp_vertices = self.vertices[:]
        temp_normals = self.normals[:]
        temp_indices = self.indices[:]

        for i in range(self.fur_density):
            temp_vertices, temp_normals, temp_indices = densify_fur(temp_vertices, temp_normals, temp_indices)

        fur_vertices = []
        for vertex, normal in zip(temp_vertices, temp_normals):
            midpoint = [vertex[0]+(normal[0]*initial_fur), vertex[1]+(normal[1]*initial_fur), vertex[2]+(normal[2]*initial_fur)]
            endpoint = [midpoint[0]+(secondary_fur*np.cos(self.fur_angle)), midpoint[1]+(secondary_fur*np.sin(self.fur_angle)), midpoint[2]+(secondary_fur)]
            fur_vertices.append([
                vertex,
                midpoint,
                endpoint,
            ])
        self.fur_vertices = fur_vertices
        
    def draw_fur(self):
        glPushMatrix()
        glBegin(GL_LINES)

        for triple in self.fur_vertices:

            glVertex3f(triple[0][0], triple[0][1], triple[0][2])
            glVertex3f(triple[1][0], triple[1][1], triple[1][2])

            glPushMatrix()
            glTranslatef(triple[1][0], triple[1][1], triple[1][2])

            glBegin(GL_LINES)
            glVertex3f(triple[1][0], triple[1][1], triple[1][2])
            glVertex3f(triple[2][0], triple[2][1], triple[2][2])
            glEnd()
            glPopMatrix()
        glEnd()
        glPopMatrix()

