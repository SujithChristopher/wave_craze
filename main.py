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

        self.spin_value = 0
        self.spin_change = 0
        
        self.previous_spin = 1
        self.current_spin = 1
        
        self.spinBox.setMinimum(1)
    
        self.spin_value_cb()
        self.init_buttons()
        
    def init_buttons(self):
        self.spinBox.valueChanged.connect(self.spin_value_cb)
        
    
    def dynamic_widgets(self):
        print('spin value',self.spin_value)
        if self.spin_change == 1:
            match self.spin_value:
                case 2:
                    self.combo_box_2 = QtWidgets.QComboBox()
                    self.combo_box_2.setObjectName("combo_box_2")
                    self.verticalLayout.addWidget(self.combo_box_2)
                    self.plot_widget_2 = pg.PlotWidget()
                    self.verticalLayout.addWidget(self.plot_widget_2)
                case 3:
                    self.combo_box_3 = QtWidgets.QComboBox()
                    self.combo_box_3.setObjectName("combo_box_3")
                    self.verticalLayout.addWidget(self.combo_box_3)
                    self.plot_widget_3 = pg.PlotWidget()
                    self.verticalLayout.addWidget(self.plot_widget_3)
                case 4:
                    self.combo_box_4 = QtWidgets.QComboBox()
                    self.combo_box_4.setObjectName("combo_box_4")
                    self.verticalLayout.addWidget(self.combo_box_4)
                    self.plot_widget_4 = pg.PlotWidget()
                    self.verticalLayout.addWidget(self.plot_widget_4)
        if self.spin_change == -1:
            self.verticalLayout.takeAt(0)
            self.verticalLayout.takeAt(0)
        
        if self.spin_change == 0:
            self.combo_box = QtWidgets.QComboBox()
            self.combo_box.setObjectName("combo_box")
            self.verticalLayout.addWidget(self.combo_box)
            self.plot_widget = pg.PlotWidget()
            self.verticalLayout.addWidget(self.plot_widget)
        

    def spin_value_cb(self):
        self.spin_value = self.spinBox.value()
        self.current_spin = self.spin_value
        self.spin_change = self.current_spin - self.previous_spin
        print(self.spin_change)
        self.previous_spin = self.current_spin
        self.dynamic_widgets()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
