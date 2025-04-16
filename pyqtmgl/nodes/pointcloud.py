from typing import Optional

import moderngl
import numpy as np

from pyqtmgl.nodes.node import Node
from pyqtmgl.cameras.camera import Camera

class Pointcloud(Node):
    def __init__(self, 
        ctx: moderngl.Context,
        points: np.ndarray,
        colors: Optional[np.ndarray]=None,
        alphas: Optional[np.ndarray]=None,
        size = 5
    ):
        """Pointcloud primitive

        Parameters
        ----------
        ctx : moderngl.Context
            The context to use
        points : np.ndarray (N, 3)
            The points to render
        colors : np.ndarray (N, 3)
            The colors of the points (RGB) ranging from 0 to 1
        alphas : np.ndarray (N,)
            The alpha values of the points ranging from 0 to 1
        """
        super().__init__(ctx, 'pointcloud')

        if colors is None:
            colors = np.ones_like(points)
        if alphas is None:
            alphas = np.ones(points.shape[0])

        self.size = size
        self.variables = {}

        self.update_variables(
            points=points, 
            colors=colors, 
            alphas=alphas,
        )

    def draw(self, camera: Camera):
        if self.n_points == 0:
            raise ValueError('No points to render')
        self.ctx.point_size = self.size
        super().draw(camera)