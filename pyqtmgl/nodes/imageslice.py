from typing import Optional

import moderngl
import numpy as np

from pyqtmgl.nodes.node import Node
from pyqtmgl.cameras.camera import Camera

class ImageSlice(Node):
    VERTEX="""
    #version 330
    uniform mat4 projection;
    uniform mat4 view;
    uniform mat4 model;
    in vec3 position;
    in vec2 uv;
    out vec2 f_uv;
    
    def main() {
        gl_Position = projection * view * model * vec4(position, 1.0);
        f_uv = uv;
    }
    """
    FRAGMENT="""
    #version 330
    uniform float min_val;
    uniform float max_val;
    uniform sampler3D im;
    uniform int dimension;
    uniform int slice;

    in vec2 f_uv;
    out vec4 color;
    def main() {
        float slice_norm;
        if (dimension == 0) {
            slice_norm = slice / im.size.x;
            coord = vec3(slice_norm, f_uv.u, f_uv.v);
        } else if (dimension == 1) {
            slice_norm = slice / im.size.y;
            coord = vec3(f_uv.u, slice_norm, f_uv.v);
        } else {
            slice_norm = slice / im.size.z;
            coord = vec3(f_uv.u, f_uv.v, slice_norm);
        }
        float val = texture(im, coord).r;
        float norm_val = clamp((val - min_val) / (max_val - min_val), 0.0, 1.0);
        color = vec4(vec3(norm_val), 1.0);
    }
    """
    REQUIRES_INDICES = True
    DRAW_MODE = moderngl.TRIANGLES
    CTX_FLAGS = moderngl.BLEND
    def __init__(self, 
        ctx: moderngl.Context,
        # points: np.ndarray,
        im: np.ndarray,
        min_val: float,
        max_val: float,
        dimension: int,
        slice: int,
        size = 5
    ):
        """Image Slice primitive

        Parameters
        ----------
        ctx : moderngl.Context
            The context to use
        points : 
        im: np.ndarray (X, Y, Z)
            The 3D image to render
        min_val: float
            The minimum value of the image
        max_val: float
            The maximum value of the image
        dimension: int
            The dimension to slice along
        slice: int
            The slice to render
        """
        super().__init__(ctx, 'ImageSlice')

        # if colors is None:
        #     colors = np.ones_like(points)
        # if alphas is None:
        #     alphas = np.ones(points.shape[0])

        self.size = size
        self.variables = {}

        self.update_variables(
            # points=points, 
            im=im,
            min_val=min_val,
            max_val=max_val,
            dimension=dimension,
            slice=slice
        )

    def update_variables(self, **kwargs):
        im = kwargs.pop('im', None)

        if im is not None:
            self.variables['im'] = im
            self.texture = self.ctx.texture(im.size)
            self.texture.use()
            self.texture.write(im.tobytes())

        min_val = kwargs.pop('min_val', None)
        max_val = kwargs.pop('max_val', None)
        dimension = kwargs.pop('dimension', None)
        slice = kwargs.pop('slice', None)
        if min_val is not None:
            self.variables['min_val'] = min_val
        if max_val is not None:
            self.variables['max_val'] = max_val
        if dimension is not None:
            self.variables['dimension'] = dimension
        if slice is not None:
            self.variables['slice'] = slice

    def prepare_vao(self):
        l, r, b, t = -1, 1, -1, 1
        data = np.array([
            l, b, 0, 0,
            r, b, 1, 0,
            r, t, 1, 1,
            l, t, 0, 1
        ], dtype='f4')
        indices = np.array([0, 1, 2, 0, 2, 3], dtype='i4')
        vbo = self.ctx.buffer(data)
        ibo = self.ctx.buffer(indices)
        self.vao = self.ctx.vertex_array(
            self.program,
            [
                (vbo, '2f 2f', 'position', 'texcoord')
            ],
            index_buffer=ibo
        )
        im = self.variables['im']
        self.program['min_val'] = self.variables.get('min_val', im.min())
        self.program['max_val'] = self.variables.get('max_val', im.max())
        self.program['dimension'] = self.variables.get('dimension', 0)
        self.program['slice'] = self.variables.get('slice', int(im.shape[0] // 2))
