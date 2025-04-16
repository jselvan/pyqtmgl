from typing import Tuple

import glm
import numpy as np


class Camera:
    def project(self, verts):
        """Project vertices to NDS"""
        projection, view = self.get_matrices()
        mvp = np.array(projection * view)
        verts = np.array(verts)
        if verts.shape[1] == 2:
            verts = np.hstack((verts, np.zeros((verts.shape[0], 1))))
        if verts.shape[1] == 3:
            verts = np.hstack((verts, np.ones((verts.shape[0], 1))))
        verts = (mvp @ verts.T).T
        verts = verts[:, :3] / verts[:, 3:]
        return verts
    def unproject(self, verts):
        """Unproject vertices from NDS"""
        projection, view = self.get_matrices()
        mvp = np.array(projection * view)
        inv_mvp = np.linalg.inv(mvp)
        # mvp = np.array(projection * view)
        verts = np.array(verts)
        if verts.shape[1] == 2:
            verts = np.hstack((verts, np.zeros((verts.shape[0], 1))))
        if verts.shape[1] == 3:
            verts = np.hstack((verts, np.ones((verts.shape[0], 1))))
        verts = verts @ inv_mvp.T
        verts = verts[:, :3] / verts[:, 3:]
        return verts

    def set_size(self, width, height):
        """
        Update the aspect ratio when the screen size changes.

        Parameters:
        width (float): New screen width.
        height (float): New screen height.
        """
        self.screen_width = width
        self.screen_height = height

    def get_matrices(self) -> Tuple[glm.mat4, glm.mat4]:
        """
        Get the current projection and view matrices.

        Returns:
        tuple: (projection_matrix, view_matrix)
        """
        return self._compute_projection_matrix(), self._compute_view_matrix()

    def _compute_projection_matrix(self) -> glm.mat4:
        raise NotImplementedError

    def _compute_view_matrix(self) -> glm.mat4:
        raise NotImplementedError