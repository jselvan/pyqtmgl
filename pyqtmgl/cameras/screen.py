import glm

from pyqtmgl.cameras.camera import Camera

class ScreenCamera(Camera):
    def __init__(self, width, height):
        self.set_size(width, height)
    def _compute_projection_matrix(self) -> glm.mat4:
        return glm.mat4(1)
    def _compute_view_matrix(self) -> glm.mat4:
        view = glm.mat4(0)
        view[0][0] = 2 / self.screen_width
        view[1][1] = -2 / self.screen_height
        view[3][0] = -1
        view[3][1] = 1
        view[3][3] = 1
        return view