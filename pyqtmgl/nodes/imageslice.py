from typing import Optional

import moderngl
import numpy as np
import glm

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
    
    void main() {
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
    uniform mat4 affine;

    in vec2 f_uv;
    out vec4 color;
    void main() {
        vec3 coord;
        vec3 imsize = textureSize(im, 0);
        if (dimension == 0) {
            coord = vec3(slice / imsize.x, f_uv.x, f_uv.y);
        } else if (dimension == 1) {
            coord = vec3(f_uv.x, slice / imsize.y, f_uv.y);
        } else {
            coord = vec3(f_uv.x, f_uv.y, slice / imsize.z);
        }
        vec3 scale = imsize / min(imsize.x, min(imsize.y, imsize.z));  // normalize by largest axis
        coord = (affine * vec4(coord, 1.0)).xyz;  // apply affine transformation
        coord /= scale;
        float val = texture(im, coord).r;

        float norm_val = clamp((val - min_val) / (max_val - min_val), 0.0, 1.0);
        color = vec4(vec3(norm_val), 1.0);
    }
    """
    REQUIRES_INDICES = True
    DRAW_MODE = moderngl.TRIANGLES
    CTX_FLAGS = moderngl.DEPTH_TEST | moderngl.BLEND
    def __init__(self, 
        ctx: moderngl.Context,
        # points: np.ndarray,
        im: Optional[np.ndarray]=None,
        affine: Optional[np.ndarray | glm.mat4]=None,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        dimension: Optional[int] = 0,
        slice: Optional[int] = None
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

        self.variables = {}
        self.width = self.height = None

        self.update_variables(
            # points=points, 
            im=im,
            affine=affine,
            min_val=min_val,
            max_val=max_val,
            dimension=dimension,
            slice=slice
        )

    def update_variables(self, **kwargs):
        im = kwargs.pop('im', None)

        if im is not None:
            
            self.variables['im'] = im = im.astype('f4')
            self.texture = self.ctx.texture3d(
                im.shape,
                1,
                im.tobytes(),
                dtype='f4',
            )
            self.texture.use(0)
            self.update_model_matrix()
        
        affine = kwargs.pop('affine', None)
        if affine is not None:
            self.variables['affine'] = glm.mat4(*affine.flatten()) if isinstance(affine, np.ndarray) else affine

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
                (vbo, '2f 2f', 'position', 'uv')
            ],
            index_buffer=ibo
        )
        im = self.variables['im']
        self.program['min_val'] = self.variables.get('min_val', im.min())
        self.program['max_val'] = self.variables.get('max_val', im.max())
        self.program['dimension'] = self.variables.get('dimension', 0)
        self.program['slice'] = self.variables.get('slice', int(im.shape[0] // 2))
        self.program['affine'].write(self.variables.get('affine', glm.mat4(1.0)).to_bytes())

    def update_model_matrix(self) -> None:
        import glm
        if self.width is None or self.height is None:
            return
        window_width, window_height = self.width, self.height
        w, h = list(set([0,1,2]) - set([self.variables['dimension']]))
        image_width = self.variables['im'].shape[w]
        image_height = self.variables['im'].shape[h]
        image_aspect = image_width / image_height
        window_aspect = window_width / window_height
        translate_x = translate_y = 0.0
        scale_x = min(1.0, 1.0 / image_aspect) / max(1.0, window_aspect)
        scale_y = min(1.0, image_aspect) * min(1.0, window_aspect)
        scale_x /= max(scale_x, scale_y)
        scale_y /= max(scale_x, scale_y)
        self.model = glm.mat4(1.0) * glm.translate(glm.vec3(translate_x, translate_y, 0)) * glm.scale(glm.vec3(scale_x, scale_y, 1.0)) 


    def set_size(self, w: int, h: int) -> None:
        # self.vao.render(self.DRAW_MODE)
        super().set_size(w, h)
        self.update_model_matrix()
