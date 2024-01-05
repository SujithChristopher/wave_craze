import pyqtgraph as pg
from PyQt6.QtWidgets import *
from PyQt6 import QtWidgets
import sys
from gui.guidesign import Ui_MainWindow
from time import sleep

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.vert_layout()
        self.init_buttons()
        self.spin_value = 0
        
    def init_buttons(self):
        self.spinBox.valueChanged.connect(self.spin_value_cb)
        
        
    def vert_layout(self):

        self.plot_widget = pg.PlotWidget()
        
        y = [5, 5, 7, 10, 3, 8, 9, 1, 6, 2]
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                
        self.verticalLayout.addWidget(self.plot_widget)
        self.plot_widget.plot(x, y, pen='r')
        
        self.combo_box = QtWidgets.QComboBox()
        self.combo_box.setObjectName("combo_box")
        self.verticalLayout.addWidget(self.combo_box)

    def spin_value_cb(self):
        self.spin_value = self.spinBox.value()
        # self.verticalLayout.removeWidget(self.plot_widget)
        # self.verticalLayout.deleteLater()
        self.verticalLayout.takeAt(0)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
