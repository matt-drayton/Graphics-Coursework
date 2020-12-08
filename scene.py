# pygame is just used to create a window with the operating system on which to draw.
import pygame

# imports all openGL functions
from OpenGL.GL import *

# import the shader class
from shaders import Shaders, Uniform

# import the camera class
from camera import Camera

# and we import a bunch of helper functions
from matutils import *

from lightSource import LightSource

import random

from FurModel import FurModel


class Scene:
    """
    This is the main class for adrawing an OpenGL scene using the PyGame library
    """

    def __init__(self, width=1920, height=1080, shaders=None):
        """
        Initialises the scene
        """

        self.window_size = (width, height)

        # by default, wireframe mode is off
        self.wireframe = False

        # the first two lines initialise the pygame window. You could use another library for this,
        # for example GLut or Qt
        pygame.init()
        screen = pygame.display.set_mode(
            self.window_size, pygame.OPENGL | pygame.DOUBLEBUF, 24
        )

        # Here we start initialising the window from the OpenGL side
        glViewport(0, 0, self.window_size[0], self.window_size[1])

        # this selects the background color
        glClearColor(0.7, 0.7, 1.0, 1.0)

        # enable back face culling (see lecture on clipping and visibility
        glEnable(GL_CULL_FACE)
        # depending on your model, or your projection matrix, the winding order may be inverted,
        # Typically, you see the far side of the model instead of the front one
        # uncommenting the following line should provide an easy fix.
        # glCullFace(GL_FRONT)

        # enable the vertex array capability
        glEnableClientState(GL_VERTEX_ARRAY)

        # enable depth test for clean output (see lecture on clipping & visibility for an explanation
        glEnable(GL_DEPTH_TEST)

        # dictionary of shaders used in this scene
        self.shaders_list = {
            # 'Phong': Shaders('phong'),# WS7
            # 'Gouraud': Shaders('gouraud'),# WS6
            # 'Flat': Shaders('flat'),# WS6
            # 'Blinn': Shaders('blinn'), # WS7
            "Fur": Shaders("fur")
        }

        # compile all shaders
        for shader in self.shaders_list.values():
            shader.compile()

        self.shaders = self.shaders_list["Fur"]

        # initialise the projective transform
        near = 1.5
        far = 20
        left = -1.0
        right = 1.0
        top = -1.0
        bottom = 1.0

        # to start with, we use an orthographic projection;
        self.P = frustumMatrix(left, right, top, bottom, near, far)

        # initialises the camera object
        self.camera = Camera(self.window_size)

        # initialise the light source
        self.light = LightSource(self, position=[5.0, 5.0, 5.0])

        # rendering mode for the shaders
        self.mode = 6  # initialise to full interpolated shading

        # This class will maintain a list of models to draw in the scene,
        self.models = []

    def add_model(self, model):
        """
        This method just adds a model to the scene.
        :param model: The model object to add to the scene
        :return: None
        """
        self.models.append(model)

    def add_models_list(self, models_list):
        """
        This method just adds a model to the scene.
        :param model: The model object to add to the scene
        :return: None
        """
        self.models.extend(models_list)

    def draw(self):
        """
        Draw all models in the scene
        :return: None
        """

        # first we need to clear the scene, we also clear the depth buffer to handle occlusions
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.camera.update()

        # then we loop over all models in the list and draw them
        for model in self.models:
            model.draw(Mp=poseMatrix(), shaders=self.shaders)
        # once we are done drawing, we display the scene
        # Note that here we use double buffering to avoid artefacts:
        # we draw on a different buffer than the one we display,
        # and flip the two buffers once we are done drawing.
        pygame.display.flip()

    def keyboard(self, event):
        if event.key == pygame.K_q:
            self.running = False

        # Camera Rotations
        elif event.key == pygame.K_LEFT:
            self.camera.phi += 0.1

        elif event.key == pygame.K_RIGHT:
            self.camera.phi -= 0.1

        elif event.key == pygame.K_UP:
            self.camera.psi -= 0.1

        elif event.key == pygame.K_DOWN:
            self.camera.psi += 0.1

        # Fur changes
        elif event.key == pygame.K_l:
            for model in self.models:
                # Only apply fur transformations if it is a fur model
                if type(model) is FurModel:
                    # Change the parameter in the existing fur model
                    model.fur_length += 0.1
                    # Create a copy so that it re-calculates vertices
                    new_fur_model = FurModel(
                        self,
                        model.initial_vertices,
                        model.initial_normals,
                        model.initial_indices,
                        model.fur_length,
                        model.fur_angle,
                        model.fur_density,
                        model.M,
                        model.material,
                        model.primitive,
                        model.visible,
                    )
                    # Add new fur model, remove old one.
                    self.models.append(new_fur_model)
                    self.models.remove(model)
                    print(
                        f"Increasing fur length to {new_fur_model.fur_length:.2f}")

        elif event.key == pygame.K_k:
            for model in self.models:
                if type(model) is FurModel:
                    model.fur_length -= 0.1
                    new_fur_model = FurModel(
                        self,
                        model.initial_vertices,
                        model.initial_normals,
                        model.initial_indices,
                        model.fur_length,
                        model.fur_angle,
                        model.fur_density,
                        model.M,
                        model.material,
                        model.primitive,
                        model.visible,
                    )
                    self.models.append(new_fur_model)
                    self.models.remove(model)
                    print(f"Decreasing fur length to {model.fur_length:.2f}")

        elif event.key == pygame.K_b:
            for model in self.models:
                if type(model) is FurModel:
                    model.fur_angle = random.randrange(0, 30)
                    new_fur_model = FurModel(
                        self,
                        model.initial_vertices,
                        model.initial_normals,
                        model.initial_indices,
                        model.fur_length,
                        model.fur_angle,
                        model.fur_density,
                        model.M,
                        model.material,
                        model.primitive,
                        model.visible,
                    )
                    self.models.append(new_fur_model)
                    self.models.remove(model)
                    print(f"Randomising fur angle to {model.fur_angle}")

        elif event.key == pygame.K_m:
            for model in self.models:
                # if model.fur_density == 1:
                #     print("Cannot increase fur density any further")
                # else:
                if type(model) is FurModel:
                    model.fur_density += 1
                    new_fur_model = FurModel(
                        self,
                        model.initial_vertices,
                        model.initial_normals,
                        model.initial_indices,
                        model.fur_length,
                        model.fur_angle,
                        model.fur_density,
                        model.M,
                        model.material,
                        model.primitive,
                        model.visible,
                    )
                    self.models.append(new_fur_model)
                    self.models.remove(model)
                    print(f"Increasing fur density to {model.fur_density}")
        elif event.key == pygame.K_n:
            for model in self.models:
                if type(model) is FurModel:
                    if model.fur_density > 0:
                        model.fur_density -= 1
                        new_fur_model = FurModel(
                            self,
                            model.initial_vertices,
                            model.initial_normals,
                            model.initial_indices,
                            model.fur_length,
                            model.fur_angle,
                            model.fur_density,
                            model.M,
                            model.material,
                            model.primitive,
                            model.visible,
                        )
                        self.models.append(new_fur_model)
                        self.models.remove(model)
                        print(f"Decreasing fur density to {model.fur_density}")
                    else:
                        print("Cannot decrease fur density any further.")
        # flag to switch wireframe rendering
        elif event.key == pygame.K_0:
            if self.wireframe:
                print("--> Rendering using colour fill")
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                self.wireframe = False
            else:
                print("--> Rendering using colour wireframe")
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                self.wireframe = True

    def pygameEvents(self):
        # check whether the window has been closed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # keyboard events
            elif event.type == pygame.KEYDOWN:
                self.keyboard(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mods = pygame.key.get_mods()
                if event.button == 4:
                    # pass
                    if mods & pygame.KMOD_CTRL:
                        self.light.position *= 1.1
                        self.light.update()
                    else:
                        self.camera.distance = max(1, self.camera.distance - 1)

                elif event.button == 5:
                    # pass
                    if mods & pygame.KMOD_CTRL:
                        self.light.position *= 0.9
                        self.light.update()
                    else:
                        self.camera.distance += 1

            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    if self.mouse_mvt is not None:
                        self.mouse_mvt = pygame.mouse.get_rel()
                        self.camera.center[0] -= (
                            float(self.mouse_mvt[0]) / self.window_size[0]
                        )
                        self.camera.center[1] -= (
                            float(self.mouse_mvt[1]) / self.window_size[1]
                        )
                    else:
                        self.mouse_mvt = pygame.mouse.get_rel()

                elif pygame.mouse.get_pressed()[2]:
                    if self.mouse_mvt is not None:
                        self.mouse_mvt = pygame.mouse.get_rel()
                        self.camera.phi -= (
                            float(self.mouse_mvt[0]) / self.window_size[0]
                        )
                        self.camera.psi -= (
                            float(self.mouse_mvt[1]) / self.window_size[1]
                        )
                    else:
                        self.mouse_mvt = pygame.mouse.get_rel()
                else:
                    self.mouse_mvt = None

    def run(self):
        """
        Draws the scene in a loop until exit.
        """

        # We have a classic program loop
        self.running = True
        while self.running:

            self.pygameEvents()

            # otherwise, continue drawing
            self.draw()
