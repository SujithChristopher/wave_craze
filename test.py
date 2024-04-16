import time
from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot, QThreadPool
from PyQt6 import QtWidgets
import pyqtgraph as pg
import sys
import toml
import serial
import struct
import numpy as np
import csv
from datetime import datetime
import serial.tools.list_ports

from gui.guidesign import Ui_MainWindow
from numba import njit

@njit
def roll(array):
    return np.roll(array, -1)

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(list)
    progress = pyqtSignal(list)

class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            pass
        else:
            pass
        finally:
            print('Thread completed')
            self.signals.finished.emit()  # Done

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.threadpool = QThreadPool()
        self.x_data = np.linspace(0, 100, 100)
        
        self.spinBox.setMinimum(1)
        self.spin_value = 1
        self.parameters = self.read_config()['parameters']
        self.dynamic_widgets()
        self.val = 0
        self.f_data = [np.zeros(100) for _ in range(4)]
        self.curve_dict = {}

        self.csv_filename = 'sensor_data.csv'
        self.csv_file = open(self.csv_filename, mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)

        self.com_box = QtWidgets.QComboBox(self.widget)
        self.com_box.setObjectName("PORT SELECTION")
        self.com_box.setGeometry(900, 0, 93, 28)
        self.select_port()
        
        self.recording = False 
        self.record_button.clicked.connect(self.toggle_record)
        self.record_button.setStyleSheet("background-color: green")

        self.time_box = QtWidgets.QComboBox(self.widget)
        self.time_box.setObjectName("time_box")
        self.time_box.setGeometry(270, 0, 151, 31)

        self.start_button.clicked.connect(self.start_program)
        self.stop_button.clicked.connect(self.stop_program)
        self.spinBox.valueChanged.connect(self.manage_widgets)
        self.time_box.activated.connect(self.select_time)

        for i, combo_box in enumerate(self.combo_boxes):
            combo_box.activated.connect(self.crv_set)
            # self.time_box.activated.connect(self.select_time)

        self.combo_boxes[1].setVisible(False)
        self.combo_boxes[2].setVisible(False)
        self.combo_boxes[3].setVisible(False)
        self.plot_widgets[1].setVisible(False)
        self.plot_widgets[2].setVisible(False)
        self.plot_widgets[3].setVisible(False)

        self.update_serial_port()
        self.update_time()
        
    def read_config(self):
        config = toml.load('config.toml')
        return config
    
    def read_sf(self):
        config = toml.load('config.toml')
        return config.get('sampling_frequency'[0], {})

    def read_y_limits(self):
        config = toml.load('config.toml')
        return config.get('y_limit', {})
    
    def select_port(self):
        ports = serial.tools.list_ports.comports()
        self.com_box.addItems([port.name for port in ports])
        self.com_box.activated.connect(self.update_serial_port)

    def select_time(self):
        self.sampling_rate = self.read_sf().get('value', 1) 
        selected_time = int(self.time_box.currentText())
        num_data_points = int(selected_time * 200)  
        self.x_range = self.sampling_rate * selected_time

        for i, combo_box in enumerate(self.combo_boxes):
            if combo_box.isVisible():
                index = combo_box.currentIndex()
                self.f_data[index] = np.roll(self.f_data[index], -num_data_points)
                self.f_data[index][:num_data_points] = 0  # Reset old data
                plot_widget = self.plot_widgets[i]
                plot_widget.setXRange(0, self.x_range)

        self.x_data = np.linspace(0, self.x_range, num_data_points)
        # self.create_curves()


    def update_time(self):
        self.time = [1, 5, 10]
        self.time_box.addItems([str(t) for t in self.time])

    def update_serial_port(self):
        self.serial_port = serial.Serial(self.com_box.currentText(), 115200)

    def toggle_record(self):
        if not self.recording:
            self.start_record()
        else:
            self.stop_record()

    def start_record(self):
        self.recording = True
        self.record_button.setStyleSheet("background-color: red")
        self.csv_writer.writerow(["Time"] + list(self.parameters.keys()))
        
        # Start recording logic here...

    def stop_record(self):
        self.recording = False
        self.record_button.setStyleSheet("background-color: green")
        self.csv_file.close()  # Close the CSV file

    def change_color(self):
        self.toggle_record()

        
    def dynamic_widgets(self):
        self.combo_boxes = []
        self.plot_widgets = []

        y_limits = self.read_y_limits()

        for i in range(4):
            combo_box = QtWidgets.QComboBox()
            combo_box.setObjectName(f"combo_box_{i+1}")
            combo_box.addItems(self.parameters.keys())
            self.verticalLayout.addWidget(combo_box, stretch=1)
            self.combo_boxes.append(combo_box)

            plot_widget = pg.PlotWidget()
            self.verticalLayout.addWidget(plot_widget, stretch=1)
            self.plot_widgets.append(plot_widget)

            if f'y{i+1}' in y_limits:
                plot_widget.setYRange(y_limits[f'y{i+1}'][0], y_limits[f'y{i+1}'][1])
            else:
                print(f"Y limits not found for index {i}")

    def manage_widgets(self):
        self.spin_value = self.spinBox.value()
        for i in range(4):
            self.combo_boxes[i].setVisible(i < self.spin_value)
            self.plot_widgets[i].setVisible(i < self.spin_value)

    def create_curve(self, plot_widget, index):
        plot_widget.clear()
        colors = ['r', 'g', 'b', 'c']
        curve = plot_widget.plot(pen=pg.mkPen(color=colors[index], width=1.5), name=f"Parameter {index+1}")
        curve.setData(self.x_data, self.f_data[index], autoDownsample=True)

        plot_widget.setXRange(self.x_data[0], self.x_data[-1])

        if index in self.curve_dict:
            self.curve_dict[index].append(curve)
        else:
            self.curve_dict[index] = [curve]

    def crv_set(self):
        for i in range(self.spin_value):
            if self.plot_widgets[i].isVisible():
                selected_index = self.combo_boxes[i].currentIndex()
                self.create_curve(self.plot_widgets[i], selected_index)

    def serial_read(self):
        if (self.serial_port.read() == b'\xff') and (self.serial_port.read() == b'\xff'):
            self.connected = True
            chksum = 255 + 255
            self.plSz = self.serial_port.read()[0]
            chksum += self.plSz
            self.payload = self.serial_port.read(self.plSz - 1)
            chksum += sum(self.payload)
            chksum = bytes([chksum % 256])
            _chksum = self.serial_port.read()
            return _chksum == chksum
        return False

    def return_str(self):
        self.total_float = 0
        self.total_int = 0

        for key in self.parameters.keys():
            if self.parameters[key] == 'float':
                self.total_float += 1
            elif self.parameters[key] == 'int':
                self.total_int += 1

        self.val = ""

        if self.total_float:
            self.val = str(self.total_float)+'f'
        if self.total_int:
            self.val = str(self.total_int)+'i'

    def unpack_values(self, progress_callback):
        while self.serial_port.is_open:
            if self.serial_read():
                try:
                    self.return_str()
                    payload_format = self.val
                    payload_size = struct.calcsize(payload_format)
                    
                    unpacked_data = struct.unpack(payload_format, self.payload[:payload_size])
                    # self.csv_writer.writerow([time.time()] + list(unpacked_data))
                    # self.csv_file.flush()  # Flush buffer to write immediately
                    progress_callback.emit(unpacked_data)
                    # print(unpacked_data)
                except struct.error as e:
                    print("Error unpacking data:", e)

    @pyqtSlot(list)
    def update_plot(self, data):
        for i in range(self.spin_value):
            if self.combo_boxes[i].isVisible():
                selected_index = self.combo_boxes[i].currentIndex()
                if selected_index < len(data):
                    parameter_name = self.combo_boxes[i].currentText()
                    if parameter_name in self.parameters:
                        index = list(self.parameters.keys()).index(parameter_name)
                        if index < len(self.f_data):
                            if len(self.f_data[index]) != len(self.x_data):
                                self.f_data[index] = np.zeros_like(self.x_data)
                            else:
                                self.f_data[index] = roll(self.f_data[index])
                            self.f_data[index][-1] = data[selected_index]

                            # Update the plot every 10 data points
                            if len(self.f_data[index]) % 10 == 0:
                                for curve in self.curve_dict.get(index, []):
                                    curve.setData(self.x_data, self.f_data[index])

    def start_program(self):
        self.worker_thread = Worker(self.unpack_values)
        self.worker_thread.signals.progress.connect(self.update_plot)
        self.worker_thread.signals.finished.connect(self.thread_complete)
        self.worker_thread.signals.error.connect(self.handle_error)
        self.threadpool.start(self.worker_thread)

    def stop_program(self):
        self.serial_port.close()
        self.threadpool.clear()

    def thread_complete(self):
        print("THREAD COMPLETED!")

    def handle_error(self, error_tuple):
        print("ERROR:", error_tuple[0])

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
