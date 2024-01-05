import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWidgets import *
import pyqtgraph as pg
from PyQt6.QtGui import *

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("PyQtGraph in PyQt6 Example")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and set a layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout(central_widget)

        # Create a pyqtgraph plot widget
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)

        # Example data for the plot
        x = [1, 2, 3, 4, 5]
        y = [2, 3, 5, 7, 11]

        # Plot the data
        self.plot_widget.plot(x, y, pen='r')

        # Button to remove the plot
        remove_button = QPushButton("Remove Plot")
        remove_button.clicked.connect(self.remove_plot)
        self.layout.addWidget(remove_button)

    def remove_plot(self):
        # Remove the pyqtgraph widget from the layout
        self.layout.removeWidget(self.plot_widget)

        # Delete the pyqtgraph widget to ensure proper cleanup
        self.plot_widget.deleteLater()
        

def main():
    app = QApplication(sys.argv)
    main_window = MyMainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
