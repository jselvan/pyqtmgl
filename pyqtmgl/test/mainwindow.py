from PyQt5.QtWidgets import QMainWindow, QDockWidget, QApplication, QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSettings

class MainWindow(QMainWindow):
    APPLICATION_NAME = "PyQt5 ModernGL Example"
    APPLICATION_VERSION = "0.1.0"
    ORGANIZATION_NAME = "pyqtmgl"
    ORGANIZATION_DOMAIN = "github.com/jselvan"

    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon.fromTheme('python3'))
        self.setWindowTitle('PyQt5 ModernGL Example')
        self.setMinimumSize(800, 600)
        self.setDockOptions(QMainWindow.AllowNestedDocks | QMainWindow.AllowTabbedDocks)

        self.menu = self.menuBar()
        file_menu = self.menu.addMenu("File")

    def add_dock_widget(self, widget: QWidget):
        name = widget.name
        parent = QDockWidget(name, self)
        parent.setObjectName(name)
        parent.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        parent.setWidget(widget)
        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea, 
            parent
        )

    def closeEvent(self, event):
        self.settings.setValue('geometry',self.saveGeometry())
        self.settings.setValue('windowState',self.saveState())
        super().closeEvent(event)
    
    def loadSettings(self):
        QApplication.setApplicationName(self.APPLICATION_NAME)
        QApplication.setOrganizationName(self.APPLICATION_VERSION)
        QApplication.setOrganizationDomain(self.ORGANIZATION_DOMAIN)
        self.settings = settings = QSettings()
        geometry = settings.value('geometry')
        if geometry is not None:
            self.restoreGeometry(geometry)
        windowState = settings.value('windowState')
        if windowState is not None:
            self.restoreState(settings.value('windowState'))
        self.update()