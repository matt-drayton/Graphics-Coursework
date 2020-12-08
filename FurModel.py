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
    def __init__(self, scene, vertices, normals, indices, fur_length=0.1, fur_angle=30, fur_density=0, M=poseMatrix(), material=None, primitive=GL_LINES, visible=True):
        '''
        Initialises the model data
        '''
        BaseModel.__init__(self, scene=scene, M=M, primitive=primitive, visible=visible)
        
        self.initial_vertices = vertices
        self.initial_normals = normals
        self.initial_indices = indices

        self.fur_length = fur_length
        self.fur_angle = fur_angle
        self.fur_density = fur_density

        self.initialise_vertices()
        # self.indices = indices

        self.vertex_colors = None
        self.material = Material(
            Ka = np.array([0.1, 0.1, 0.2], 'f'),
            Kd = np.array([0.1, 0.5, 0.1], 'f'),
            Ks = np.array([0.9, 0.9, 1.0], 'f'),
            Ns = 10.0
        )
        self.bind()


    def initialise_vertices(self):
        new_vertices = np.zeros_like(self.initial_vertices)
        new_normals = np.zeros_like(self.initial_normals)
        for vertex, normal in zip(self.initial_vertices, self.initial_normals):
            new_vertices = np.vstack((new_vertices, vertex))
            new_vertices = np.vstack((new_vertices, vertex + (normal * self.fur_length)))
            new_normals = np.vstack((new_normals, normal))
            new_normals = np.vstack((new_normals, normal))

        self.vertices = new_vertices
        self.normals = new_normals

    
    # def generate_fur_vertices(self):
    #     initial_fur = self.fur_length / 3
    #     secondary_fur = self.fur_length / (2/3)
        
    #     # Deep copy
    #     temp_vertices = self.vertices[:]
    #     temp_normals = self.normals[:]
    #     temp_indices = self.indices[:]

    #     for i in range(self.fur_density):
    #         temp_vertices, temp_normals, temp_indices = densify_fur(temp_vertices, temp_normals, temp_indices)

    #     fur_vertices = []
    #     for vertex, normal in zip(temp_vertices, temp_normals):
    #         midpoint = [vertex[0]+(normal[0]*initial_fur), vertex[1]+(normal[1]*initial_fur), vertex[2]+(normal[2]*initial_fur)]
    #         endpoint = [midpoint[0]+(secondary_fur*np.cos(self.fur_angle)), midpoint[1]+(secondary_fur*np.sin(self.fur_angle)), midpoint[2]+(secondary_fur)]
    #         fur_vertices.append([
    #             vertex,
    #             midpoint,
    #             endpoint,
    #         ])
    #     self.vertices = fur_vertices
        
    # def draw_fur(self):
    #     glPushMatrix()
    #     glBegin(GL_LINES)

    #     for triple in self.fur_vertices:

    #         glVertex3f(triple[0][0], triple[0][1], triple[0][2])
    #         glVertex3f(triple[1][0], triple[1][1], triple[1][2])

    #         glPushMatrix()
    #         glTranslatef(triple[1][0], triple[1][1], triple[1][2])

    #         glBegin(GL_LINES)
    #         glVertex3f(triple[1][0], triple[1][1], triple[1][2])
    #         glVertex3f(triple[2][0], triple[2][1], triple[2][2])
    #         glEnd()
    #         glPopMatrix()
    #     glEnd()
    #     glPopMatrix()

def densify_fur(vertices, normals, indices):
    new_vertices = vertices[:]
    new_normals = normals[:]
    new_indices = indices[:]

    vertex_faces = []
    normal_faces = []
    for index in indices:
        vertex_faces.append([vertices[index[0]], vertices[index[1]], vertices[index[2]]])
        normal_faces.append([normals[index[0]], normals[index[1]], normals[index[2]]])

    for index, vertex_face in zip(indices, vertex_faces):
        centroid_x = (vertex_face[0][0] + vertex_face[1][0] + vertex_face[2][0]) / 3
        centroid_y = (vertex_face[0][1] + vertex_face[1][1] + vertex_face[2][1]) / 3
        centroid_z = (vertex_face[0][2] + vertex_face[1][2] + vertex_face[2][2]) / 3
        centroid = [centroid_x, centroid_y, centroid_z]

        new_vertices = np.vstack((new_vertices, centroid))
        last_index = len(new_vertices) - 1
        new_face1 = [index[0], index[1], last_index]
        new_face2 = [index[0], index[2], last_index]
        new_face3 = [index[1], index[2], last_index]
        new_indices = np.vstack((new_indices, new_face1))
        new_indices = np.vstack((new_indices, new_face2))
        new_indices = np.vstack((new_indices, new_face3))


    for normal_face in normal_faces:
        centroid_x = (normal_face[0][0] + normal_face[1][0] + normal_face[2][0]) / 3
        centroid_y = (normal_face[0][1] + normal_face[1][1] + normal_face[2][1]) / 3
        centroid_z = (normal_face[0][2] + normal_face[1][2] + normal_face[2][2]) / 3
        centroid = [centroid_x, centroid_y, centroid_z]
        new_normals = np.vstack((new_normals, centroid))

    return new_vertices, new_normals, new_indices

