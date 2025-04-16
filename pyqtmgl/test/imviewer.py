from PyQt5 import QtCore, QtWidgets

from pyqtmgl.glwidget import GLWidget
from pyqtmgl.nodes.imageslice import ImageSlice
from pyqtmgl.test.runner import run_dockable

class CustomSlider(QtWidgets.QWidget):
    handleValueChange = QtCore.pyqtSignal(int)
    def __init__(self, label, value=None, range=None, **kwargs):
        super(CustomSlider, self).__init__(**kwargs)
        self.label = QtWidgets.QLabel(label)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.valueChanged.connect(self.handleSliderValueChange)
        self.numbox = QtWidgets.QSpinBox()
        self.numbox.valueChanged.connect(self.handleNumboxValueChange)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.label, 0)
        layout.addWidget(self.numbox)
        layout.addWidget(self.slider)

        if range is not None:
            self.setRange(*range)
        if value is not None:
            self.setValue(value)

    @QtCore.pyqtSlot(int)
    def handleSliderValueChange(self, value):
        self.numbox.setValue(value)
        self.handleValueChange.emit(value)

    @QtCore.pyqtSlot(int)
    def handleNumboxValueChange(self, value):
        # Prevent values outside slider range
        if value < self.slider.minimum():
            self.numbox.setValue(self.slider.minimum())
        elif value > self.slider.maximum():
            self.numbox.setValue(self.slider.maximum())

        self.slider.setValue(self.numbox.value())
        self.handleValueChange.emit(value)
    
    def setRange(self, min, max):
        self.slider.setRange(min, max)
        self.numbox.setRange(min, max)
    
    def setValue(self, value):
        self.slider.setValue(value)
        self.numbox.setValue(value)
    
    def value(self):
        return self.slider.value()


class ImageViewerWidget(GLWidget):
    def __init__(self, image=None):
        super().__init__()
        self.image = image
    def init(self):
        self.im = ImageSlice(self.ctx)
        if self.image is not None:
            self.set_data(self.image)
    def set_data(self, image):
        self.image = image
        self.im.update_variables(im=image)
    @property
    def nodes(self):
        yield self.image
    def render(self):
        pass
    def set_min_value(self, value):
        print(f"Min value: {value}")
    def set_max_value(self, value):
        print(f"Max value: {value}")

class ImageViewer(QtWidgets.QWidget):
    name = "Image Viewer"
    def __init__(self):
        super().__init__()
        im_range = -1000, 1000

        self.glwidget = ImageViewerWidget()
        self.minValueSlider = CustomSlider(
            "Min Value", 
            range=im_range,
            value=0
        )
        self.minValueSlider.handleValueChange.connect(self.glwidget.set_min_value)
        self.maxValueSlider = CustomSlider(
            "Max Value",
            range=im_range,
            value=255
        )
        self.maxValueSlider.handleValueChange.connect(self.glwidget.set_max_value)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.glwidget, 1)
        self.layout.addWidget(self.minValueSlider, 0)
        self.layout.addWidget(self.maxValueSlider, 0)
        self.setLayout(self.layout)

def main():
    run_dockable([ImageViewer])

if __name__ == '__main__':
    main()