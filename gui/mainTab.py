from PySide6.QtCore import *
from PySide6.QtWidgets import *

class MainTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        self.setObjectName("MainTab")
        self.resize(1096, 850)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.label = QLabel(self)
        self.label.setObjectName("label")
        self.label.setText("Windows")
        self.horizontalLayout.addWidget(self.label)

        self.spinBox = QSpinBox(self)
        self.spinBox.setObjectName("spinBox")
        self.spinBox.setMaximum(4)
        self.spinBox.setMinimum(1)
        self.spinBox.setFixedHeight(30)
        self.spinBox.setFixedWidth(100)
        self.horizontalLayout.addWidget(self.spinBox)

        self.com_port_label = QLabel(self)
        self.com_port_label.setObjectName("com_port_label")
        self.com_port_label.setText("COM Port:")
        self.horizontalLayout.addWidget(self.com_port_label)

        self.com_port_combo = QComboBox(self)
        self.com_port_combo.setObjectName("com_port_combo")
        self.com_port_combo.setFixedHeight(30)
        self.com_port_combo.setFixedWidth(100)
        self.horizontalLayout.addWidget(self.com_port_combo)

        # Add the seconds selection combo box to the horizontal layout
        self.seconds_label = QLabel(self)
        self.seconds_label.setObjectName("seconds_label")
        self.seconds_label.setText("Seconds:")
        self.horizontalLayout.addWidget(self.seconds_label)

        self.seconds_combo = QComboBox(self)
        self.seconds_combo.setObjectName("seconds_combo")
        self.seconds_combo.setFixedHeight(30)
        self.seconds_combo.setFixedWidth(100)
        self.horizontalLayout.addWidget(self.seconds_combo)

        # Add the buttons to the horizontal layout
        self.start_button = QPushButton(self)
        self.start_button.setStyleSheet("background-color: rgb(155, 170, 200);")
        self.start_button.setObjectName("start_button")
        self.start_button.setText("Start")
        self.start_button.setFixedHeight(30)
        self.start_button.setFixedWidth(100)
        self.horizontalLayout.addWidget(self.start_button)

        self.stop_button = QPushButton(self)
        self.stop_button.setStyleSheet("background-color: rgb(155, 170, 200);")
        self.stop_button.setObjectName("stop_button")
        self.stop_button.setText("Stop")
        self.stop_button.setFixedHeight(30)
        self.stop_button.setFixedWidth(100)
        self.horizontalLayout.addWidget(self.stop_button)

        self.record_button = QPushButton(self)
        self.record_button.setStyleSheet("background-color: rgb(155, 170, 200);")
        self.record_button.setObjectName("record_button")
        self.record_button.setText("Record")
        self.record_button.setFixedHeight(30)
        self.record_button.setFixedWidth(100)
        self.horizontalLayout.addWidget(self.record_button)

        # Create an empty vertical layout for the bottom section
        self.plot_layout = QVBoxLayout()
        self.plot_layout.setObjectName("plot_layout")
        self.verticalLayout.addLayout(self.plot_layout)

        # Set the layout for the MainTab
        self.setLayout(self.verticalLayout)