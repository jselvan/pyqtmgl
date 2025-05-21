from typing import Tuple, Optional, Dict

import numpy as np
from numpy.typing import ArrayLike

from pyqtmgl.glwidget import GLWidget
from pyqtmgl.nodes.pointcloud import Pointcloud
from pyqtmgl.nodes.line import Line
from pyqtmgl.nodes.node import Node
from pyqtmgl.cameras import RectCamera, ScreenCamera


class GraphWidget(GLWidget):
    name = "Graph"

    def __init__(self):
        super().__init__()
        self.nodes_by_name: Dict[str, Node] = {}
        self.camera = None
        self.screen_camera = None
        self.bg = (1.0, 1.0, 1.0, 1.0)
        self._camera_rect = None

    @property
    def nodes(self):
        return list(self.nodes_by_name.values())

    @property
    def cameras(self):
        return [self.camera, self.screen_camera]

    def init(self):
        self.camera = RectCamera(rect=[0, 0, 1, 1])
        self.set_rect()
        self.screen_camera = ScreenCamera(self.width(), self.height())
    
    def set_rect(self, rect: Optional[ArrayLike]=None):
        """Set the camera rect to the given values."""
        if rect is None:
            if self.rect is None:
                rect = [0, 0, 1, 1]
            else:
                rect = self._camera_rect
        if self.camera is not None:
            self.camera.rect = rect
        self._camera_rect = rect

    def add_node(self, name: str, node: Node):
        """Add a new node (e.g., Pointcloud or Line) with a unique name."""
        self.nodes_by_name[name] = node
    
    def add_scatter(self, name: str, **kwargs):
        """Add a scatter node with the given name and parameters."""
        if name in self.nodes_by_name:
            raise KeyError(f"Node with name '{name}' already exists.")
        node = Pointcloud(self.ctx, **kwargs)
        self.add_node(name, node)

    def add_line(self, name: str, **kwargs):
        """Add a line node with the given name and parameters."""
        if name in self.nodes_by_name:
            raise KeyError(f"Node with name '{name}' already exists.")
        node = Line(self.ctx, **kwargs)
        self.add_node(name, node)

    def remove_node(self, name: str):
        """Remove a node by name."""
        if name in self.nodes_by_name:
            del self.nodes_by_name[name]

    def update_node(self, name: str, **kwargs):
        """Update the specified node's variables (e.g., points, colors, etc.)"""
        if name not in self.nodes_by_name:
            raise KeyError(f"No node named '{name}' exists.")
        node = self.nodes_by_name[name]
        node.update_variables(**kwargs)

    def set_camera_from_points(self, points: np.ndarray):
        """Update the camera rect to fit given 2D points."""
        if self.camera and points.size > 0:
            self.camera.rect = [
                np.min(points[:, 0]), np.min(points[:, 1]),
                np.max(points[:, 0]), np.max(points[:, 1])
            ]

    def get_mouse_in_data_coords(self, pos) -> Tuple[float, float]:
        if self.camera is None or self.screen_camera is None:
            raise ValueError("Camera not initialized")
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
        if self.camera is None:
            raise ValueError("Camera not initialized")
        for node in self.nodes_by_name.values():
            if node.n_points == 0:
                continue
            node.draw(self.camera)
