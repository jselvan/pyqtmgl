from typing import Optional, List, Mapping

from PyQt5 import QtCore, QtWidgets, QtGui
import numpy as np

from pyqtmgl.glwidget import GLWidget
from pyqtmgl.cameras.rect import RectCamera
from pyqtmgl.nodes.linecollection import LineCollection

DEFAULT_CHUNK_SIZE = 1e4
WHITE = [1, 1, 1]
RED = [1, 0, 0]
class ContinuousViewer(GLWidget):
    name = "Continuous Viewer"

    def __init__(self, points=None, colours=None):
        super().__init__()
        self.points = points
        self.colours = colours

    def init(self):
        self.line = LineCollection(self.ctx)
        self.camera = RectCamera()
        if self.points is not None:
            self.set_data(self.points, self.colours)
        
        self.actions: Mapping[str, QtWidgets.QAction] = {}
        self.actions["scroll_forward"] = QtWidgets.QAction("Scroll Forward", self)
        self.actions["scroll_backward"] = QtWidgets.QAction("Scroll Backward", self)
        self.actions["scroll_forward"].triggered.connect(lambda: self.move(1))
        self.actions["scroll_backward"].triggered.connect(lambda: self.move(-1))
        self.actions["scroll_forward"].setShortcut(QtCore.Qt.Key_Right) 
        # self.actions["scroll_forward"].setShortcutContext(QtCore.Qt.ApplicationShortcut)
        self.actions["scroll_backward"].setShortcut(QtCore.Qt.Key_Left)

        for action in self.actions.values():
            self.addAction(action)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.actions["scroll_forward"].trigger()
        else:
            self.actions["scroll_backward"].trigger()

    def move(self, direction):
        stepsize = 1e3
        if self.points is None:
            return
        if direction == -1:
            self.startidx = int(max(0, self.startidx - stepsize))
        elif direction == 1:
            self.startidx = int(min(self.points.shape[1] - self.chunklength, self.startidx + stepsize))
        else:
            raise ValueError("Direction must be -1 or 1")
        self.update_trace()

    def set_data(self, points, colours=None):
        self.points = np.asarray(points)
        if colours is None:
            self.colours = None
        else:
            self.colours = np.asarray(colours)
        self.startidx = 0
        self.chunklength = int(min(DEFAULT_CHUNK_SIZE, self.points.size))
        self.scale = self.points.max()
        self.update_trace()
    
    def update_trace(self):
        chunkslice = slice(self.startidx, self.startidx+self.chunklength)
        points = self.points[:, chunkslice]
        n_lines, n_points = points.shape[:2]
        if self.colours is not None:
            colours = self.colours[:, chunkslice, :]
        else:
            colours = np.ones((n_lines, n_points, 3))

        self.camera.set_rect(
            [0, -self.scale, self.chunklength, 2 * self.scale * n_lines]
        )
        self.line.update_variables(
            lines=points,
            vertex_colors=colours.reshape(-1, 3),
            offset=self.scale*2,
        )
        self.update()
    
    @property
    def nodes(self):
        return [self.line]
    
    @property
    def cameras(self):
        return [self.camera]
    
    def render(self):
        self.ctx.clear()
        if self.points is None:
            return
        self.line.draw(self.camera)
