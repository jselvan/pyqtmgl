import glm

from pyqtmgl.cameras.camera import Camera

class RectCamera(Camera):
    def __init__(self, rect=None):
        if rect is None:
            rect = [0, 0, 1, 1]
        self.set_rect(rect)
    def set_rect(self, rect):
        """Set the rect attribute of the camera.

        Parameters
        ----------
        rect : Sequence[float] of length 4
            left, bottom, right, top
        """
        self.rect = rect
    def _compute_projection_matrix(self):
        return glm.ortho(self.rect[0], self.rect[2], self.rect[1], self.rect[3], -1, 1)
    def _compute_view_matrix(self):
        return glm.mat4(1)
    def zoom(self, factor_x: float, factor_y: float):
        cx = (self.rect[0] + self.rect[2]) / 2
        cy = (self.rect[1] + self.rect[3]) / 2
        dx = (self.rect[2] - self.rect[0]) / 2
        dy = (self.rect[3] - self.rect[1]) / 2
        new_dx = dx / factor_x
        new_dy = dy / factor_y
        self.rect = [cx - new_dx, cy - new_dy, cx + new_dx, cy + new_dy]