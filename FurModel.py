# imports all openGL functions
from OpenGL.GL import *

# and we import a bunch of helper functions
from matutils import *

from material import Material
from BaseModel import BaseModel


class FurModel(BaseModel):
    """
    Fur model. Can be instansiated with the vertices, normals, and indices from any model. Will create a separate mesh that adds fur. 
    """

    def __init__(self, scene, vertices, normals, indices, fur_length=0.2, fur_angle=0, fur_density=0, M=poseMatrix(), material=None, primitive=GL_LINES, visible=True):
        """
        Initialises the model data
        """
        BaseModel.__init__(self, scene=scene, M=M,
                           primitive=primitive, visible=visible)

        # Stores initial values to allow for paramaters to be changed back and forwards
        self.initial_vertices = vertices
        self.initial_normals = normals
        self.initial_indices = indices

        # Fur parameters
        self.fur_length = fur_length
        self.fur_angle = fur_angle
        self.fur_density = fur_density

        self.initialise_vertices()

        self.vertex_colors = None

        # Sets the colour of the fur.
        self.material = Material(
            Ka=np.array([67/255, 45/255, 31/255], "f"),
            Kd=np.array([75/255, 63/255, 34/255], "f"),
            Ks=np.array([176/255, 119/255, 85/255], "f"),
            Ns=10.0,
        )
        self.bind()

    def initialise_vertices(self):
        '''
        Initialises the vertices that will be rendered according to the fur parameters
        '''
        # Create a deep copy so that the initials are not modified
        initial_vertices_copy = self.initial_vertices[:]
        initial_normals_copy = self.initial_normals[:]
        initial_indices_copy = self.initial_indices[:]

        # Separates the fur into a short straight section followed by a longer angled section
        fur_length_a = self.fur_length / 3
        fur_length_b = self.fur_length * (2/3)

        # Applies the fur densifier. Creates new vertices in the middle of triangles / quads for more fur
        for i in range(self.fur_density):
            additional_vertices, additional_normals = self.densify_fur(
                initial_vertices_copy, initial_normals_copy, initial_indices_copy)

            initial_vertices_copy = np.vstack(
                (initial_vertices_copy, additional_vertices))
            initial_normals_copy = np.vstack(
                (initial_normals_copy, additional_normals))

        # Initialises the vertices and normals with 0's
        new_vertices = np.zeros_like(initial_vertices_copy)
        new_normals = np.zeros_like(initial_normals_copy)

        for vertex, normal in zip(initial_vertices_copy, initial_normals_copy):
            # Add the current vertex
            new_vertices = np.vstack((new_vertices, vertex))
            # Find the midpoint of the hair by going from the current vertex in the normal direction by the fur length.
            midpoint = vertex + (normal * fur_length_a)

            # Initialise the endpoint of the fur. Angle it in the direction of the fur.
            endpoint = midpoint

            # Calculate the endpoint's actual location
            endpoint[0] += (np.cos(self.fur_angle) *
                            np.cos(self.fur_angle) * fur_length_b)

            endpoint[1] += (np.sin(self.fur_angle) * fur_length_b)

            endpoint[2] += fur_length_b * \
                np.sin(self.fur_angle) * np.cos(self.fur_angle)

            # Add the vertices to the buffer as required
            new_vertices = np.vstack((new_vertices, midpoint))
            new_vertices = np.vstack((new_vertices, midpoint))
            new_vertices = np.vstack((new_vertices, endpoint))

            new_normals = np.vstack((new_normals, normal))
            new_normals = np.vstack((new_normals, normal))

        self.vertices = new_vertices
        self.normals = new_normals

    def curvy_hair(self, vertex, normal, vertices, normals, fur_length):
        '''
        Deprecated fancy hair function. Created a smoother arc for the fur but was too resource intensive :(
        :param vertex: The midpoint of the fur
        :param normal: The normal vector of the vertex
        :param vertices: List of vertices to append new fur points to
        :param normals: List of normals to append new fur normals to
        :param fur_length: The length of the fur

        '''
        a1 = 0
        a2 = 0
        while a1 < self.angle1:
            while a2 < self.angle2:
                vertices = np.vstack(
                    (vertices, vertex))
                new_point = vertex
                new_point[0] += normal[0] * \
                    fur_length * np.cos(a1) * np.cos(a2)
                new_point[1] += normal[1] * fur_length * np.sin(a2)
                new_point[2] += normal[2] * \
                    fur_length * np.cos(a1) * np.sin(a2)
                a1 += 15
                a2 += 15
                vertices = np.vstack(
                    (vertices, new_point))
        return vertices

    def get_face_vertices(self, vertices, indices):
        '''
        From a list of vertices and indices, return a list of faces. 
        :param vertices: The list of vertices to draw from
        :param indices: The corresponding list of indices representing faces
        '''
        faces = []
        for index in indices:
            face = []
            for i in index:
                face.append(vertices[i])
            faces.append(face)
        return np.array(faces)

    def get_centroid(self, face):
        '''
        From a face list, return the centroid point.
        :param face: The list of vectors representing a face
        '''
        return sum(face) / len(face)

    def densify_fur(self, vertices, normals, indices):
        '''
        Returns a new list of vertex and normals. Each face is split into smaller segments at the center.
        :param vertices: The list of indices to densify 
        :param normals: The corresponding list of normals to densify
        :param indices: The corresponding list of indices representing faces to densify
        '''
        vertex_faces = self.get_face_vertices(vertices, indices)
        normal_faces = self.get_face_vertices(normals, indices)

        vertex_centroids = np.zeros_like(vertices)
        normal_centroids = np.zeros_like(normals)

        for index, vertex_face, normal_face in zip(indices, vertex_faces, normal_faces):
            vertex_centroid = sum(vertex_face) / len(vertex_face)
            normal_centroid = sum(normal_face) / len(normal_face)

            vertex_centroids = np.vstack((vertex_centroids, vertex_centroid))
            normal_centroids = np.vstack((normal_centroids, normal_centroid))

        return vertex_centroids, normal_centroids
