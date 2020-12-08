# imports all openGL functions
from OpenGL.GL import *

# and we import a bunch of helper functions
from matutils import *

from material import Material

class BaseModel:
    '''
    Base class for all models, implementing the basic draw function for triangular meshes.
    Inherit from this to create new models.
    '''

    def __init__(self, scene, M=poseMatrix(), color=[1.,1.,1.], primitive=GL_TRIANGLES, visible=True):
        '''
        Initialises the model data
        '''

        print('+ Initializing {}'.format(self.__class__.__name__))

        # if this flag is set to False, the model is not rendered
        self.visible = visible

        # store the scene reference
        self.scene = scene

        # store the type of primitive to draw
        self.primitive = primitive

        # store the object's color (deprecated now that we have per-vertex colors)
        self.color = color

        self.vertices = None
        self.indices = None
        self.normals = None
        self.vertex_colors = None

        # material
        self.material = Material(
            Ka = np.array([0.1, 0.1, 0.2], 'f'),
            Kd = np.array([0.1, 0.5, 0.1], 'f'),
            Ks = np.array([0.9, 0.9, 1.0], 'f'),
            Ns = 10.0
        )

        # dict of VBOs
        self.vbos = {}

        # dict of attributes
        self.attributes = {}

        # store the position of the model in the scene, ...
        self.M = M

        self.fur_length = 0.1
        self.fur_angle = 0
        self.fur_density = 0
        self.fur_vertices = None

    def initialise_vbo(self, name, data):
        print('Initialising VBO for attribute {}'.format(name))

        # bind the GLSL program to find the attribute locations
        #glUseProgram(self.scene.shaders.program)

        # bind the location of the attribute in the GLSL program to the next index
        # the name of the location must correspond to a 'in' variable in the GLSL vertex shader code
        self.attributes[name] = len(self.vbos)

        if data is None:
            print('(W) Warning in {}.bind_attribute(): Data array for attribute {} is None!'.format(
                self.__class__.__name__, name))
            return

        # create a buffer object...
        self.vbos[name] = glGenBuffers(1)
        # and bind it
        glBindBuffer(GL_ARRAY_BUFFER, self.vbos[name])

        # ... and we set the data in the buffer as the vertex array
        glBufferData(GL_ARRAY_BUFFER, data, GL_STATIC_DRAW)

        # enable the attribute
        glEnableVertexAttribArray(self.attributes[name])

        # Associate the bound buffer to the corresponding input location in the shader
        # Each instance of the vertex shader will get one row of the array
        # so this can be processed in parallel!
        glVertexAttribPointer(index=self.attributes[name], size=data.shape[1], type=GL_FLOAT, normalized=False,
                              stride=0, pointer=None)



    def bind_all_attributes(self):
        '''
        bind all VBOs to the corresponding attributes in the shader program. Call this before rendering.
        '''
        for attribute in self.vbos:
            # bind the buffer corresponding to the attribute
            glBindBuffer(GL_ARRAY_BUFFER,self.vbos[attribute])

            # enable the attribute
            glEnableVertexAttribArray(self.attributes[attribute])


    def bind(self):
        '''
        This method stores the vertex data in a Vertex Buffer Object (VBO) that can be uploaded
        to the GPU at render time.
        '''

        # We use a Vertex Array Object to pack all buffers for rendering in the GPU (see lecture on OpenGL)
        self.vao = glGenVertexArrays(1)

        # bind the VAO to retrieve all buffers and rendering context
        glBindVertexArray(self.vao)

        if self.vertices is None:
            print('(W) Warning in {}.bind(): No vertex array!'.format(self.__class__.__name__))

        # initialise vertex position VBO and link to shader program attribute
        self.initialise_vbo('position', self.vertices)
        self.initialise_vbo('normal', self.normals)
        self.initialise_vbo('color', self.vertex_colors)

        # if indices are provided, put them in a buffer too
        if self.indices is not None:
            self.index_buffer = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices, GL_STATIC_DRAW)

        # bind all attributes to the correct locations in the VAO
        for name in self.attributes:
            glBindAttribLocation(self.scene.shaders.program, self.attributes[name], name)
            print('Binding attribute {} to location {}'.format(name,self.attributes[name]))

        # finally we unbind the VAO and VBO when we're done to avoid side effects
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER,0)

        self.generate_fur_vertices()


    def draw(self, Mp, shaders):
        '''
        Draws the model using OpenGL functions
        :return:
        '''

        if self.visible:

            if self.vertices is None:
                print('(W) Warning in {}.draw(): No vertex array!'.format(self.__class__.__name__))


            # tell OpenGL to use this shader program for rendering
            glUseProgram(shaders.program)

            # setup the shader program and provide it the Model, View and Projection matrices to use
            # for rendering this model
            shaders.bind(
                P = self.scene.P,
                V = self.scene.camera.V,
                M = np.matmul(Mp,self.M),
                mode = self.scene.mode,
                material=self.material,
                light=self.scene.light
            )

            # bind the Vertex Array Object so that all buffers are bound correctly and the following operations affect them
            glBindVertexArray(self.vao)

            # check whether the data is stored as vertex array or index array
            if self.indices is not None:
                # draw the data in the buffer using the index array
                glDrawElements(self.primitive, self.indices.flatten().shape[0], GL_UNSIGNED_INT, None )
                pass
            else:
                # draw the data in the buffer using the vertex array ordering only.
                glDrawArrays(self.primitive, 0, self.vertices.shape[0])

            # unbind the shader to avoid side effects
            glBindVertexArray(0)
            self.draw_fur()



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


def __del__(self):
    '''
    Release all VBO objects when finished.
    '''
    for vbo in self.vbos.items():
        glDeleteBuffers(1,vbo)


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

