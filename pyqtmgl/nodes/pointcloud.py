from typing import Optional

import moderngl
import numpy as np
from numpy.typing import ArrayLike

from pyqtmgl.nodes.node import Node
from pyqtmgl.cameras.camera import Camera

class Pointcloud(Node):
    def __init__(self, 
        ctx: Optional[moderngl.Context],
        points: Optional[np.ndarray]=None,
        colors: Optional[ArrayLike]=None,
        alphas: Optional[ArrayLike]=None,
        size = 5,
        **kwargs
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

        self.size = size
        self.variables = {}

        self.update_variables(
            points=points, 
            colors=colors, 
            alphas=alphas,
            **kwargs
        )

    def draw(self, camera: Camera):
        if self.ctx is None:
            raise ValueError('Context not initialized')
        if self.n_points == 0:
            raise ValueError('No points to render')
        self.ctx.point_size = self.size
        super().draw(camera)