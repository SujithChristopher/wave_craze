from PySide6.QtCore import *
from PySide6.QtWidgets import *


class mathTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        self.setObjectName("functionTab")
        self.resize(1096, 850)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.dropdown1 = QComboBox(self)
        self.dropdown1.setObjectName("dropdown1")
        self.dropdown1.setFixedHeight(30)
        self.dropdown1.setFixedWidth(100)
        self.horizontalLayout.addWidget(self.dropdown1)

        # Add a QLabel with + symbol
        plus_label = QLabel("+")
        plus_label.setObjectName("plus_label")
        self.horizontalLayout.addWidget(plus_label)

        self.dropdown2 = QComboBox(self)
        self.dropdown2.setObjectName("dropdown2")
        self.dropdown2.setFixedHeight(30)
        self.dropdown2.setFixedWidth(100)
        self.horizontalLayout.addWidget(self.dropdown2)

        # Add a QLabel with = symbol
        equal_label = QLabel("=")
        equal_label.setObjectName("equal_label")
        self.horizontalLayout.addWidget(equal_label)

        self.add_button = QPushButton(self)
        # self.add_button.setGeometry(QRect(580, 520, 93, 28))
        self.add_button.setFixedHeight(30)
        self.add_button.setFixedWidth(100)
        self.add_button.setStyleSheet("background-color: rgb(7, 117, 127);")
        self.add_button.setObjectName("Add")
        self.add_button.setText("Add ")
        self.horizontalLayout.addWidget(self.add_button)

        self.plot_layout = QVBoxLayout()
        self.plot_layout.setObjectName("plot_layout")
        self.verticalLayout.addLayout(self.plot_layout)
