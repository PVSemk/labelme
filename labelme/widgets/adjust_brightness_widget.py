from qtpy.QtCore import Qt
from qtpy import QtGui
from qtpy import QtWidgets

from PIL import Image
from PIL import ImageEnhance


class AdjustBrightnessContrastWidget(QtWidgets.QDialog):
    def __init__(self, filename, prev_shapes, callback, parent=None):
        super(AdjustBrightnessContrastWidget, self).__init__(parent)
        self.setModal(True)
        self.setWindowTitle('Brightness/Contrast')

        self.slider0 = self._create_slider()
        self.slider1 = self._create_slider()

        formLayout = QtWidgets.QFormLayout()
        formLayout.addRow(self.tr('Brightness'), self.slider0)
        formLayout.addRow(self.tr('Contrast'), self.slider1)
        self.setLayout(formLayout)

        self.img = Image.open(filename).convert('RGBA')
        self.shapes = prev_shapes
        self.callback = callback

    def on_new_value(self, value):
        brightness = self.slider0.value() / 100
        contrast = self.slider1.value() / 100

        img = self.img
        img = ImageEnhance.Brightness(img).enhance(brightness)
        img = ImageEnhance.Contrast(img).enhance(contrast)

        bytes = img.tobytes('raw', 'RGBA')
        qimage = QtGui.QImage(bytes,
                              img.size[0], img.size[1],
                              QtGui.QImage.Format_RGB32).rgbSwapped()
        self.callback(qimage, self.shapes)

    def _create_slider(self):
        slider = QtWidgets.QSlider(Qt.Horizontal)
        slider.setRange(0, 300)
        slider.setValue(100)
        slider.valueChanged.connect(self.on_new_value)
        return slider
