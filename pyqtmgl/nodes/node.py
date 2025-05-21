from typing import List, Optional, SupportsFloat

import moderngl
import numpy as np

from pyqtmgl.cameras import Camera

class Node:
    VERTEX="""
    #version 330
    uniform mat4 projection;
    uniform mat4 view;
    uniform mat4 model;
    in vec3 position;
    in vec3 color;
    in float alpha;
    out vec4 f_color;
    void main() {
        gl_Position = projection * view * model * vec4(position, 1.0);
        f_color = vec4(color, alpha);
    }
    """
    FRAGMENT="""
    #version 330
    in vec4 f_color;
    out vec4 color;
    void main() {
        color = f_color;
    }
    """
    GEOMETRY = None
    REQUIRES_INDICES = False
    CTX_FLAGS = moderngl.DEPTH_TEST | moderngl.BLEND
    DRAW_MODE = moderngl.POINTS

    def __init__(self, ctx: Optional[moderngl.Context], name):
        if ctx is None:
            self.ctx = None
        else:
            self.set_context(ctx)
        self.name = name
        self.children: List[Node] = []
        self._is_3d = True
        self.model = None
        self.n_points = 0

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def set_context(self, ctx: moderngl.Context):
        self.ctx = ctx
        self.compile_program()
        if not hasattr(self, 'children'):
            return
        for child in self.children:
            child.set_context(ctx)

    def compile_program(self):
        if self.ctx is None:
            raise ValueError('No context set')
        self.program = self.ctx.program(
            vertex_shader=self.VERTEX,
            fragment_shader=self.FRAGMENT,
            geometry_shader=self.GEOMETRY
        )

    def add(self, node: 'Node'):
        self.children.append(node)

    def set_size(self, width, height):
        self.width = width
        self.height = height

    def update_variables(self, **kwargs):
        points = kwargs.pop('points', None)
        if points is None and any(dim in kwargs for dim in ['x', 'y', 'z']):
            x = kwargs.pop('x', None)
            y = kwargs.pop('y', None)
            z = kwargs.pop('z', None)
            if x is None:
                if y is None:
                    raise ValueError("x and y cannot both be None")
                else:
                    y = np.asarray(y)
                x = np.arange(len(y))
            elif y is None:
                x = np.asarray(x)
                y = np.arange(len(x))
            else:
                x = np.asarray(x)
                y = np.asarray(y)
            if x.shape != y.shape:
                raise ValueError("x and y must have the same shape")
            if z is None:
                z = np.zeros_like(x)
            else:
                z = np.asarray(z)
            if x.shape != z.shape:
                raise ValueError("x and z must have the same shape")
            points = np.array([x, y, z]).T
            self.variables['points'] = points

        elif points is not None:
            points = np.asarray(points)
            if points.ndim == 1:
                points = points[:, None]
            if points.ndim != 2:
                raise ValueError(
                    'Points must have two dimensions with'\
                    'the second dimension being one of [1,2,3]'
                )

            if points.shape[1] == 1:
                # we add a linear x coordinate
                # and we add a zero z coordinate
                self._is_3d = False
                x = np.arange(points.shape[0])
                points = np.concatenate(
                    [
                        x[:, None], 
                        points, 
                        np.zeros((points.shape[0], 1))
                    ], 
                    axis=1)
            elif points.shape[1] == 2:
                self._is_3d = False
                points = np.concatenate(
                    [
                        points, 
                        np.zeros((points.shape[0], 1))
                    ], 
                    axis=1)
            elif points.shape[1] == 3:
                self._is_3d = True
            else:
                raise ValueError('Points must be of shape, (N, 1), (N, 2) or (N, 3)')
            if 'points' not in self.variables or points.shape[0] != self.variables['points'].shape[0]:
                # clear variables if points have changed
                self.variables = {}
            self.variables['points'] = points

        if 'points' in self.variables:
            n_points = self.variables['points'].shape[0]
        else:
            n_points = 0
        self.n_points = n_points

        zorder = kwargs.pop('zorder', None)
        if self._is_3d and zorder is not None:
            raise ValueError('Zorder is not supported in 3D')
        if zorder is not None and zorder.shape[0] != n_points:
            raise ValueError('Zorder must be of shape (N,)')
        if 'points' in self.variables and not self._is_3d and zorder is not None:
            # z = np.argsort(-zorder)
            z = (zorder / zorder.max()) # normalize to [-1, 1]
            self.variables['points'][:, 2] = z

        colors = kwargs.pop('colors', None)
        if colors is not None:
            colors = np.asarray(colors)
            if colors.ndim == 1:
                colors = np.repeat(colors[None, :], n_points, axis=0)
            if colors.shape[1] != 3:
                raise ValueError('Colors must be of shape (N, 3)')
            self.variables['colors'] = colors
        if self.variables.get('colors') is None:
            self.variables['colors'] = np.ones((n_points, 3))
        
        alphas = kwargs.pop('alphas', None)
        if alphas is not None:
            if np.isscalar(alphas):
                if not isinstance(alphas, SupportsFloat):
                    raise ValueError('Alphas must be a scalar or an array')
                alphas = np.ones(n_points) * float(alphas)
            else:
                alphas = np.asarray(alphas)
            if alphas.shape[0] != n_points:
                raise ValueError('Alphas must be of shape (N,)')
            self.variables['alphas'] = alphas[:, None]
        if self.variables.get('alphas') is None:
            self.variables['alphas'] = np.ones((n_points, 1))

        indices = kwargs.pop('indices', None)
        if indices == 'auto':
            indices = np.arange(n_points, dtype='i4')
            indices = np.stack([indices[:-1], indices[1:]], axis=1).flatten()
        if indices is not None:
            # if indices.shape[1] != 2:
            #     raise ValueError('Indices must be of shape (N, 2)')
            self.variables['indices'] = np.asarray(indices, dtype='i4')
        if 'indices' not in self.variables and self.REQUIRES_INDICES:
            indices = np.arange(n_points, dtype='i4')
            indices = np.stack([indices[:-1], indices[1:]], axis=1).flatten()
            self.variables['indices'] = indices

        for variable, value in kwargs.items():
            self.variables[variable] = value

    def _prepare_camera_uniforms(self, camera: Camera) -> None:
        projection, view = camera.get_matrices()
        self.program['projection'].write(projection.to_bytes()) # type: ignore
        self.program['view'].write(view.to_bytes()) # type: ignore
        if self.model is not None:
            self.program['model'].write(self.model.to_bytes()) # type: ignore
        else:
            self.program['model'] = np.eye(4, dtype='f4').flatten()

    def draw(self, camera: Camera) -> None:
        if self.ctx is None:
            raise ValueError('No context set')
        self.prepare_vao()
        if not self.vao is None:
            self._prepare_camera_uniforms(camera)
            self.ctx.enable(self.CTX_FLAGS)
            self.vao.render(self.DRAW_MODE)
        for child in self.children:
            child.draw(camera)

    def prepare_vao(self) -> None:
        """Get the vertex array object
        """
        if self.ctx is None:
            raise ValueError('No context set')
        data = np.concatenate([
            self.variables['points'], 
            self.variables['colors'], 
            self.variables['alphas']
        ], axis=1)
        if len(data) == 0:
            self.vao = None
        vbo = self.ctx.buffer(data.astype('f4').tobytes())
        if self.REQUIRES_INDICES:
            ibo = self.ctx.buffer(self.variables['indices'].astype('i4').tobytes())
        else:
            ibo = None
        self.vao = self.ctx.vertex_array(
            self.program,
            [
                (vbo, '3f 3f 1f', 'position', 'color', 'alpha')
            ],
            index_buffer=ibo
        )
