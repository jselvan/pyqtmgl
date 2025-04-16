from typing import Optional

import moderngl
import numpy as np

from pyqtmgl.nodes.node import Node

class Line(Node):
    REQUIRES_INDICES = True
    DRAW_MODE = moderngl.LINES
    GEOMETRY = """
    #version 330
    layout(lines) in;
    layout(triangle_strip, max_vertices = 4) out;

    uniform float linewidth;

    in vec4 f_color[];  // Color from vertex shader
    out vec4 g_color;

    void main() {
        vec2 p0 = gl_in[0].gl_Position.xy;
        vec2 p1 = gl_in[1].gl_Position.xy;

        // Compute the direction of the line in screen space
        vec2 dir = normalize(p1 - p0);
        vec2 perp = vec2(-dir.y, dir.x); // Perpendicular vector

        // Offset for line width (assuming clip space [-1,1])
        vec2 offset = perp * (linewidth / 2000.0);

        g_color = f_color[0];
        gl_Position = vec4(p0 + offset, 0.0, 1.0);
        EmitVertex();

        g_color = f_color[0];
        gl_Position = vec4(p0 - offset, 0.0, 1.0);
        EmitVertex();

        g_color = f_color[1];
        gl_Position = vec4(p1 + offset, 0.0, 1.0);
        EmitVertex();

        g_color = f_color[1];
        gl_Position = vec4(p1 - offset, 0.0, 1.0);
        EmitVertex();

        EndPrimitive();
    }
    """
    FRAGMENT = """
    #version 330
    in vec4 g_color;
    out vec4 fragColor;
    void main() {
        fragColor = g_color;
    }
    """
    def __init__(self, 
        ctx: moderngl.Context,
        points: Optional[np.ndarray]=None,
        colors: Optional[np.ndarray]=None,
        alphas: Optional[np.ndarray]=None,
        indices: Optional[np.ndarray]=None,
        size = 1
    ):
        """Line primitive

        Parameters
        ----------
        ctx : moderngl.Context
            The context to use
        points : np.ndarray (N, 2|3)
            The points to render
        colors : np.ndarray (N, 3)
            The colors of the points (RGB) ranging from 0 to 1
        alphas : np.ndarray (N,)
            The alpha values of the points ranging from 0 to 1
        """
        super().__init__(ctx, 'line')

        self.n_points = 0
        self.size = size
        self.variables = {}
        self.update_variables(
            points=points, 
            colors=colors, 
            alphas=alphas,
            indices=indices)

    def draw(self, camera):
        if self.n_points == 0:
            raise ValueError('No points to render')
        self.program['linewidth'] = self.size
        super().draw(camera)