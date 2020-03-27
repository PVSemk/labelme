from qtpy import QtCore
from qtpy import QtWidgets


class BrightnessWidget(QtWidgets.QSlider):

    def __init__(self, value=0):
        super(BrightnessWidget, self).__init__(QtCore.Qt.Horizontal)
        self.setMinimum(-100)
        self.setMaximum(100)
        self.setValue(value)
        self.setToolTip('Brightness Level')
        self.setStatusTip(self.toolTip())
        self.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.setTickInterval(25)


class ContrastWidget(QtWidgets.QSlider):

    def __init__(self, value=100):
        super(ContrastWidget, self).__init__(QtCore.Qt.Horizontal)
        self.setMinimum(0)
        self.setMaximum(300)
        self.setValue(value)
        self.setToolTip('Contrast Level')
        self.setStatusTip(self.toolTip())
        self.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.setTickInterval(50)

    def value(self):
        return float(super().value()) / 100

