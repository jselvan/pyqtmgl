
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

import numpy as np

from pyqtmgl.glwidget import GLWidget
from pyqtmgl.nodes.pointcloud import Pointcloud
from pyqtmgl.cameras import RectCamera, ScreenCamera
from pyqtmgl.test.runner import run_dockable

class ScatterWidget(GLWidget):
    name = "Scatter"
    @property
    def nodes(self):
        return [self.scatter]
    @property
    def cameras(self):
        return [self.camera, self.screen_camera]
    def init(self):
        self.scatter = Pointcloud(
            self.ctx, 
            np.random.rand(1000, 2), 
            size=10,
            colors=[1, 0, 0]
        )
        self.camera = RectCamera(rect=[0, 0, 2, 1])
        self.screen_camera = ScreenCamera(self.width(), self.height())

    def get_mouse_in_data_coords(self, pos):
        pos = np.array([[pos.x(), pos.y()]])
        x, y = self.camera.unproject(self.screen_camera.project(pos)[:, :2])[0, :2]
        return x, y

    def mouseMoveEvent(self, event):
        cursor = event.pos()
        x, y = self.get_mouse_in_data_coords(cursor)
        tooltip_text = f"Cursor at ({float(x):.2f}, {float(y):.2f})"
        self.set_tooltip(tooltip_text, cursor)
        super().mouseMoveEvent(event)

    def render(self):
        self.scatter.draw(self.camera)


def main():
    run_dockable([ScatterWidget])

if __name__ == '__main__':
    main()