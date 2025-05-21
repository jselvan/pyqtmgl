from typing import Sequence
from pyqtmgl.cameras.screen import ScreenCamera
from pyqtmgl.nodes.node import Node
from pyqtmgl.cameras import Camera

import moderngl
from PyQt5.QtWidgets import QOpenGLWidget, QToolTip
from PyQt5.QtGui import QSurfaceFormat

class GLWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.ctx = None
        self.screen = None
        self.bg = (0.0, 0.0, 0.0, 1.0)

        fmt = QSurfaceFormat()
        fmt.setVersion(4, 3)
        fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        fmt.setSamples(4)
        self.setFormat(fmt)
        self.setMouseTracking(True)  # Enable tracking for mouse move events

    @property
    def nodes(self) -> Sequence[Node]:
        return []

    @property
    def cameras(self) -> Sequence[Camera]:
        return []

    def initializeGL(self) -> None:
        self.ctx = moderngl.create_context()
        self.screen_camera = ScreenCamera(self.width(), self.height())
        self.init()

    def update_context(self) -> None:
        for node in self.nodes:
            if node is not None and node.ctx is None:
                node.set_context(self.ctx)

    def paintGL(self) -> None:
        self.update_context()
        self.screen = self.ctx.detect_framebuffer(self.defaultFramebufferObject())
        self.screen.use()
        self.makeCurrent()
        self.ctx.clear(*self.bg)
        self.render()

    def resizeGL(self, w: int, h: int) -> None:
        self.ctx.viewport = (0, 0, w, h)
        for node in self.nodes:
            if node is not None:
                node.set_size(w, h)
        for camera in self.cameras:
            if camera is not None:
                camera.set_size(w, h)

    def init(self) -> None:
        pass

    def render(self) -> None:
        pass

    def set_tooltip(self, text: str, pos):
        QToolTip.showText(self.mapToGlobal(pos), text, self)
    
    def on_mouse_move(self, event):
        pass