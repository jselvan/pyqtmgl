from typing import Sequence

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt

from pyqtmgl.test.mainwindow import MainWindow

def run_dockable(widgets: Sequence[QWidget], *args, **kwargs) -> None:
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    app = QApplication([])
    window = MainWindow()
    for widget in widgets:
        window.add_dock_widget(widget(*args, **kwargs))
    window.loadSettings()
    window.show()
    app.exec_()