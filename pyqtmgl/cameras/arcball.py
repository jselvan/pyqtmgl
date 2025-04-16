from enum import Enum
from typing import Optional

import glm
import numpy as np

from pyqtmgl.cameras.camera import Camera

class CameraView(Enum):
    XY_POS = 0
    XY_NEG = 1
    XZ_POS = 2
    XZ_NEG = 3
    YZ_POS = 4
    YZ_NEG = 5

class ArcballCamera(Camera):
    def __init__(self, screen_size, fov=60.0, near=0.1, far=10.0):
        """
        Initialize the ArcballCamera.

        Parameters:
        fov (float): Field of view in degrees.
        aspect (float): Aspect ratio (width / height).
        near (float): Near clipping plane.
        far (float): Far clipping plane.
        """

        self.fov = np.radians(fov)
        self.screen_width, self.screen_height = screen_size
        self.near = near
        self.far = far

        self._mouse_sensitivity = 2

        # Default camera parameters
        self.target = glm.vec3(0, 0, 0)
        self.distance = 2
        self.forward = glm.vec3(0, 0, -1)
        self.right = glm.vec3(1, 0, 0)
        self.up = glm.vec3(0, 1, 0)
        self.save_defaults()

    def save_defaults(self):
        self.defaults = {
            'target': self.target,
            'distance': self.distance,
            'forward': self.forward,
            'right': self.right,
            'up': self.up,
        }

    def reset(self):
        """Reset the camera to its default position."""
        self.target = self.defaults['target']
        self.distance = self.defaults['distance']
        self.forward = self.defaults['forward']
        self.right = self.defaults['right']
        self.up = self.defaults['up']

    def _compute_projection_matrix(self) -> glm.mat4:
        """Compute the perspective projection matrix."""
        aspect = self.screen_width / self.screen_height
        projection = glm.perspective(self.fov, aspect, self.near, self.far)
        # allow toggling to orthographic projection
        # projection = glm.ortho(-1, 1, -1, 1, self.near, self.far)
        return projection

    def _compute_view_matrix(self) -> glm.mat4:
        """Compute the view matrix."""
        # Calculate the camera position
        rotation = glm.transpose(glm.mat3(self.right, self.up, -self.forward))
        translate = glm.mat4(1)
        translate[3] = glm.vec4(-self.position, 1)
        view = glm.mat4(rotation) * translate
        return view

    @property
    def position(self):
        return self.target - self.distance * self.forward

    def set_rotation(self, yaw: float, pitch: float):
        yaw, pitch = np.radians(yaw), np.radians(pitch)
        forward = glm.vec3(
            np.cos(yaw) * np.cos(pitch), 
            np.sin(pitch), 
            np.sin(yaw) * np.cos(pitch))
        self._update_vectors(forward)
    
    def _update_vectors(self, forward: glm.vec3, up: Optional[glm.vec3] = None):
        self.forward = glm.normalize(forward)
        self.right = glm.normalize(glm.cross(self.forward, up or self.up))
        self.up = glm.normalize(glm.cross(self.right, self.forward))

    # def set_view(self, forward: glm.vec3, up: glm.vec3):
    #     self._update_vectors(forward, up)
    
    def set_view(self, view: CameraView):
        UP = glm.vec3(0, 1, 0)
        FORWARD = glm.vec3(0, 0, -1)
        RIGHT = glm.vec3(1, 0, 0)

        if view == CameraView.XY_POS:
            self._update_vectors(FORWARD, UP)
        elif view == CameraView.XY_NEG:
            self._update_vectors(-FORWARD, UP)
        elif view == CameraView.XZ_POS:
            self._update_vectors(-UP, -FORWARD)
        elif view == CameraView.XZ_NEG:
            self._update_vectors(UP, FORWARD)
        elif view == CameraView.YZ_POS:
            self._update_vectors(-RIGHT, UP)
        elif view == CameraView.YZ_NEG:
            self._update_vectors(RIGHT, UP)

    def set_target(self, target: glm.vec3):
        self.target = target

    def rotate_mouse(self, dx, dy):
        """Rotate the camera around the target using mouse input."""
        theta_x = -dx * self._mouse_sensitivity * np.pi / self.screen_width
        theta_y = -dy * self._mouse_sensitivity * np.pi / self.screen_height
        rotation = glm.mat4()
        rotation = glm.rotate(rotation, theta_x, self.up)
        rotation = glm.rotate(rotation, theta_y, self.right)
        forward = glm.vec4(self.forward, 0)
        forward = rotation * forward
        # fix gimbal lock by rotating around the right vector when pitch is near 90 degrees
        if abs(glm.dot(forward.xyz, self.up)) > 0.99:
            rotation = glm.rotate(rotation, theta_y, self.right)
            forward = rotation * forward
        self._update_vectors(forward.xyz)

    def translate_mouse(self, dx, dy):
        """
        Translate the camera target.

        Parameters:
        dx (float): Mouse movement in x.
        dy (float): Mouse movement in y.
        """
        translation_speed = .01
        dx_scaled = -dx * translation_speed * self.right
        dy_scaled = dy * translation_speed * self.up
        self.set_target(self.target + dx_scaled + dy_scaled)

    def zoom(self, delta_scroll):
        """
        Zoom the camera in and out.

        Parameters:
        delta_scroll (float): Scroll delta (positive to zoom in, negative to zoom out).
        """
        zoom_speed = 0.01
        self.distance = max(0.1, self.distance + (delta_scroll * zoom_speed))

    def get_matrices(self):
        """
        Get the current projection and view matrices.

        Returns:
        tuple: (projection_matrix, view_matrix)
        """
        return self._compute_projection_matrix(), self._compute_view_matrix()