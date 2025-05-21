from PyQt5 import QtCore, QtWidgets, QtGui

from pyqtmgl.glwidget import GLWidget
from pyqtmgl.nodes.imageslice import ImageSlice
from pyqtmgl.cameras.rect import RectCamera
from pyqtmgl.test.runner import run_dockable

from pyqtmgl.nodes.line import Line
import numpy as np
class RectTool:
    def __init__(self, ctx):
        self.ctx = ctx
        self.corner1 = None
        self.corner2 = None
        self.line = Line(self.ctx)
    def set_start(self, point):
        self.corner1 = point
    def set_end(self, point):
        self.corner2 = point
        # the four corners of the rectangle
    def reset(self):
        self.corner1 = None
        self.corner2 = None
    def get_rect(self):
        x1, y1 = self.corner1
        x2, y2 = self.corner2
        z = 1
        verts = np.array([[x1, y1, z], [x2, y1, z], [x2, y2, z], [x1, y2, z]])
        indices = np.array([[0, 1], [1, 2], [2, 3], [3, 0]])
        return verts, indices
    def draw(self, camera):
        if self.corner1 is None or self.corner2 is None:
            return
        verts, indices = self.get_rect()
        self.line.update_variables(points=verts, indices=indices)
        self.line.draw(camera)


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
    def __init__(self, image=None, affine=None):
        super().__init__()
        self.image = image
        self.affine = affine
        self.tool_active = False
        self.actions = {}
        self.actions['ResetCamera'] = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_H), self)
        self.actions['ResetCamera'].activated.connect(self.reset_camera)
        self.actions['ResetCamera'].setEnabled(True)
        self.actions['ResetCamera'].setContext(QtCore.Qt.WidgetShortcut)
    def init(self):
        self.im = ImageSlice(self.ctx, dimension=1, slice=250, min_val=0, max_val=255)
        if self.image is not None:
            self.set_data(self.image, self.affine)
        self.camera = RectCamera(rect=[-1, -1, 1, 1])
        self.tool = RectTool(self.ctx)
        # create a shortcut that will reset camera to the original view
    def reset_camera(self):
        self.camera.set_rect([-1, -1, 1, 1])
        print("resetting camera")
        self.update()

    def set_data(self, image, affine=None):
        self.image = image
        self.affine = affine
        self.im.update_variables(im=image, affine=affine)
    @property
    def nodes(self):
        yield self.im
        yield self.tool.line
    @property
    def cameras(self):
        yield self.camera
        yield self.screen_camera
    def render(self):
        if self.image is not None:
            self.im.draw(self.camera)
        if self.tool_active:
            self.tool.draw(self.camera)
    def set_min_value(self, value):
        self.im.update_variables(min_val=value)
        self.update()
    def set_max_value(self, value):
        self.im.update_variables(max_val=value)
        self.update()
    def set_slice_value(self, value):
        self.im.update_variables(slice=value)
        self.update()
    def get_mouse_in_data_coords(self, pos):
        pos = np.array([[pos.x(), pos.y()]])
        x, y = self.camera.unproject(self.screen_camera.project(pos)[:, :2])[0, :2]
        return x, y
    def mousePressEvent(self, event):
        mousepos = self.get_mouse_in_data_coords(event.pos())
        if event.button() == QtCore.Qt.LeftButton:
            if self.tool_active:
                self.tool.set_end(mousepos)
                self.update()
                self.tool_active = False
                if self.tool.corner1 is not None and self.tool.corner2 is not None:
                    l = min(self.tool.corner1[0], self.tool.corner2[0])
                    r = max(self.tool.corner1[0], self.tool.corner2[0])
                    b = min(self.tool.corner1[1], self.tool.corner2[1])
                    t = max(self.tool.corner1[1], self.tool.corner2[1])

                    # make bl, tr have aspect ratio of 1
                    width, height = r - l, t - b
                    if width < height:
                        # make it square
                        l = l - (height - width) / 2
                        r = r + (height - width) / 2
                    else:
                        b = b - (width - height) / 2
                        t = t + (width - height) / 2
                    self.camera.set_rect([l, b, r, t])
                    self.tool.reset()
                    QtCore.QTimer.singleShot(100, self.update)
            else:
                self.tool.set_start(mousepos)
                self.tool_active = True
                self.update()
    def mouseMoveEvent(self, event):
        if self.tool_active:
            mousepos = self.get_mouse_in_data_coords(event.pos())
            self.tool.set_end(mousepos)
            self.update()

class ImageViewer(QtWidgets.QWidget):
    name = "Image Viewer"
    def __init__(self, image=None, affine=None):
        super().__init__()
        im_range = -1000, 1000

        self.glwidget = ImageViewerWidget(image=image, affine=affine)
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

        self.sliceSlider = CustomSlider(
            "Slice",
            range=(0, 512),
            value=250
        )
        self.sliceSlider.handleValueChange.connect(self.glwidget.set_slice_value)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.glwidget, 1)
        self.layout.addWidget(self.minValueSlider, 0)
        self.layout.addWidget(self.maxValueSlider, 0)
        self.layout.addWidget(self.sliceSlider, 0)
        self.setLayout(self.layout)

def main():
    impath = "D:/Analysis/Scripts/tract_viewer/toto/T1_pre2post_grid_resample.nii.gz"
    impath = "D:/Analysis/Scripts/tract_viewer/toto/T1_post_grid_resample.nii.gz"
    import nibabel as nib
    import glm
    im = nib.load(impath)
    affine = glm.mat4(1) #* glm.rotate(-90, glm.vec3(0, 0, 1))
    imdata = im.get_fdata()
    # print(imdata.shape) 
    # imdata = np.rot90(imdata, 1, [0,2])
    # print(imdata.shape) 

    # import numpy as np
    # img = np.random.rand(512, 512, 256) * 255
    # img = img.astype('f4')
    run_dockable([ImageViewer], image=imdata, affine=affine)

if __name__ == '__main__':
    main()