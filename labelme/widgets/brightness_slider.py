from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets


class BrightnessWidget(QtWidgets.QSlider):

    def __init__(self, value=0):
        super(BrightnessWidget, self).__init__(QtCore.Qt.Vertical)
        self.setMinimum(-100)
        self.setMaximum(100)
        self.setValue(value)
        self.setToolTip('Brightness Level')
        self.setStatusTip(self.toolTip())
        self.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.setTickInterval(50)

    def minimumSizeHint(self):
        height = super(BrightnessWidget, self).minimumSizeHint().height()
        fm = QtGui.QFontMetrics(self.font())
        width = fm.width(str(self.maximum()))
        return QtCore.QSize(width, height)
