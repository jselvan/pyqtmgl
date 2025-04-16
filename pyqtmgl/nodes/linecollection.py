from pyqtmgl.nodes.line import Line
from pyqtmgl.nodes.node import Node
import numpy as np

class LineCollection(Line):
    def __init__(self, ctx, lines=None, colors=None, alphas=None, zorder=None, offset=None, size=1):
        """LineCollection primitive

        Parameters
        ----------
        ctx : moderngl.Context
            The context to use
        lines : np.ndarray (N_LINES, N_POINTS, 1-3)
            The lines to render
        vertex_colors : np.ndarray (N_LINES*N_POINTS, 3)
            The colors of the points (RGB) ranging from 0 to 1
        colors : np.ndarray (N_LINES, 3)
            The colors of the lines (RGB) ranging from 0 to 1
        alphas : np.ndarray (N_LINES,)
            The alpha values of the lines ranging from 0 to 1
        width : float
            The width of the lines
        """
        Node.__init__(self, ctx, 'linecollection')
    
        self.n_lines = 0
        self.n_points_per_line = 0
        self.n_points = 0
        self.size = size
        
        self.variables = {}
        if lines is not None:
            self.update_variables(
                lines=lines, 
                colors=colors, 
                alphas=alphas,
                zorder=zorder,
                offset=offset
            )

    def update_variables(self, **kwargs):
        # we want to process the the arguments from lines to points
        # and then pass the rest to the super class
        lines = kwargs.pop('lines', None)
        offset = kwargs.pop('offset', None)
        if lines is None:
            if 'points' not in self.variables:
                raise ValueError('You must provide lines')
        else:
            if lines.ndim == 2:
                lines = lines[:, :, None]
            if lines.ndim != 3:
                raise ValueError('Lines must have 2 or 3 dimensions')
            if lines.shape[2] == 1:
                # we add a linear x coordinate
                # and we add a zero z coordinate
                self._is_3d = False
                x = np.arange(lines.shape[1])
                x = np.expand_dims(x, axis=(0, 2))
                x = np.broadcast_to(x, lines.shape)
                z = np.zeros(lines.shape)
                lines = np.concatenate(
                    [
                        x,
                        lines, 
                        z
                    ],
                    axis=2
                )
            elif lines.shape[2] == 2:
                self._is_3d = False
                lines = np.concatenate(
                    [
                        lines, 
                        np.zeros((lines.shape[0], lines.shape[1], 1))
                    ],
                    axis=2
                )
            elif lines.shape[2] != 3:
                raise ValueError('Lines must be of shape, (L, P, 1), (L, P, 2) or (L, P, 3)')
            self.n_lines = lines.shape[0]
            self.n_points_per_line = lines.shape[1]
            self.n_points = self.n_lines * self.n_points_per_line

            if offset is not None:
                if np.isscalar(offset):
                    offset = np.arange(self.n_lines) * offset
                if offset.size != self.n_lines:
                    raise ValueError('Size mismatch between offset and lines')
                lines[:, :, 1] += offset[:, None]
        
            points = lines.reshape(self.n_points, 3)
            self.variables['points'] = points

        # for colour, alpha, and width, we repeat the values for each point
        colors = kwargs.pop('colors', None)
        vertex_colors = kwargs.pop('vertex_colors', None)
        if colors is not None and vertex_colors is not None:
            raise ValueError('You can only provide one of colors or vertex_colors')
        elif colors is None and vertex_colors is None:
            colors = np.ones((self.n_points, 3))
        elif vertex_colors is not None:
            if vertex_colors.shape[0] != self.n_points:
                raise ValueError('Size mismatch between vertex_colors and points')
            colors = vertex_colors
        elif colors is not None:
            if colors.ndim == 1 and colors.shape[0] == 3:
                colors = np.tile(colors, (self.n_points, 1))
            elif colors.ndim == 2 and colors.shape[1] == 3:
                colors = np.repeat(colors, self.n_points_per_line, axis=0)
            else:
                raise ValueError('Colors must be of shape (3,) or (N, 3)')
        kwargs['colors'] = colors

        alphas = kwargs.pop('alphas', None)
        if alphas is None:
            alphas = np.ones(self.n_points)
        elif alphas.ndim == 0:
            alphas = np.repeat(alphas, self.n_lines)
        elif alphas.shape[0] == self.n_lines:
            alphas = np.repeat(alphas, self.n_points_per_line)
        else:
            raise ValueError('Size mismatch between alphas and lines')
        kwargs['alphas'] = alphas

        zorder = kwargs.pop('zorder', None)
        if zorder is None:
            zorder = np.ones(self.n_points)
        elif zorder.shape[0] == self.n_lines:
            zorder = np.repeat(zorder, self.n_points_per_line)
        else:
            raise ValueError('Size mismatch between zorder and lines')
        kwargs['zorder'] = zorder

        # we need to construct the indices for the lines
        lineidx = np.arange(self.n_points_per_line, dtype=np.int32)
        lineidx = np.stack([lineidx[:-1], lineidx[1:]], axis=1) # (P-1, 2)
        offset = np.arange(self.n_lines, dtype=np.int32) * self.n_points_per_line # (L,)
        idx = np.expand_dims(offset, axis=(1,2)) + np.expand_dims(lineidx, axis=0) # (L, P-1, 2)
        kwargs['indices'] = idx.reshape(-1, 2)

        return super().update_variables(**kwargs)