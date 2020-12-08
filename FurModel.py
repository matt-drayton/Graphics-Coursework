# imports all openGL functions
from OpenGL.GL import *

# and we import a bunch of helper functions
from matutils import *

from material import Material
from BaseModel import BaseModel


class FurModel(BaseModel):
    """
    Base class for all models, implementing the basic draw function for triangular meshes.
    Inherit from this to create new models.
    """

    def __init__(self, scene, vertices, normals, indices, fur_length=0.1, fur_angle=30, fur_density=0, M=poseMatrix(), material=None, primitive=GL_LINES, visible=True,):
        """
        Initialises the model data
        """
        BaseModel.__init__(self, scene=scene, M=M,
                           primitive=primitive, visible=visible)

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
            Ka=np.array([67/255, 45/255, 31/255], "f"),
            Kd=np.array([75/255, 63/255, 34/255], "f"),
            Ks=np.array([176/255, 119/255, 85/255], "f"),
            Ns=10.0,
        )
        self.bind()

    def initialise_vertices(self):
        initial_vertices_copy = self.initial_vertices[:]
        initial_normals_copy = self.initial_normals[:]
        initial_indices_copy = self.initial_indices[:]

        for i in range(self.fur_density):
            additional_vertices, additional_normals = densify_fur(
                initial_vertices_copy, initial_normals_copy, initial_indices_copy)

            initial_vertices_copy = np.vstack(
                (initial_vertices_copy, additional_vertices))
            initial_normals_copy = np.vstack(
                (initial_normals_copy, additional_normals))

        new_vertices = np.zeros_like(initial_vertices_copy)
        new_normals = np.zeros_like(initial_normals_copy)

        for vertex, normal in zip(initial_vertices_copy, initial_normals_copy):
            new_vertices = np.vstack((new_vertices, vertex))
            new_vertices = np.vstack(
                (new_vertices, vertex + (normal * self.fur_length)))
            new_normals = np.vstack((new_normals, normal))
            new_normals = np.vstack((new_normals, normal))

        self.vertices = new_vertices
        self.normals = new_normals


def get_face_vertices(vertices, indices):
    faces = []
    for index in indices:
        face = []
        for i in index:
            face.append(vertices[i])
        faces.append(face)
    return np.array(faces)


def get_centroid(face):
    return sum(face) / len(face)


def add_to_buffer(buffer, old_face, new_centroid):
    buffer = np.vstack((buffer, new_centroid))
    return buffer


def densify_fur(vertices, normals, indices):
    vertex_faces = get_face_vertices(vertices, indices)
    normal_faces = get_face_vertices(normals, indices)

    vertex_centroids = np.zeros_like(vertices)
    normal_centroids = np.zeros_like(normals)

    for index, vertex_face, normal_face in zip(indices, vertex_faces, normal_faces):
        vertex_centroid = sum(vertex_face) / len(vertex_face)
        normal_centroid = sum(normal_face) / len(normal_face)

        vertex_centroids = add_to_buffer(
            vertex_centroids, vertex_face, vertex_centroid)

        normal_centroids = add_to_buffer(
            normal_centroids, normal_face, normal_centroid)
    return vertex_centroids, normal_centroids
