import time
from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot, QThreadPool
from PyQt6.QtWidgets import QMainWindow, QTabWidget
import pyqtgraph as pg
import sys
import toml
import serial
import struct
import numpy as np
import csv
from datetime import datetime
from test_code import *
import serial.tools.list_ports
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6 import QtWidgets

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
        Initialize the runner function with passed args, kwargs.
        '''
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            self.signals.error.emit((e,))
        else:
            if result is not None:  # Only emit result if it's not None
                self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class MainWindow(QMainWindow):
    data_saved = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.viewTab = MainTab()
        self.settingsTab = SettingTab()

        self.tabs.addTab(self.viewTab, "Realtime View")
        self.tabs.addTab(self.settingsTab, "Settings")

        self.threadpool = QThreadPool()
        self.x_data = np.linspace(0, 100, 100)
        
        self.viewTab.spinBox.setMinimum(1)
        self.spin_value = 1
        self.parameters = self.read_config()['parameters']
        self.sampling_frequency = self.read_config()['sampling_frequency']
        self.dynamic_widgets()
        self.val = 0
        self.f_data = [np.zeros(100) for _ in range(4)]
        self.curve_dict = {}

        self.csv_filename = 'sensor_data.csv'
        self.csv_file = open(self.csv_filename, mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)

        self.select_port()
        
        self.trigger = 0
        self.worker_thread = None
        self.stop_thread = False
        
        self.recording = False 
        self.viewTab.record_button.clicked.connect(self.toggle_record)
        self.viewTab.record_button.setStyleSheet("background-color: green")

        self.settingsTab.save_button.clicked.connect(self.handle_stop)
        self.viewTab.spinBox.valueChanged.connect(self.manage_widgets)
        self.viewTab.seconds_combo.activated.connect(self.select_time)
        self.settingsTab.add_button.clicked.connect(self.add_rows)
        self.settingsTab.save_button.clicked.connect(self.save_data)
        self.settingsTab.tableWidget.setHorizontalHeaderLabels(["Sensor ", "Data Type"])
        self.data_saved.connect(self.update_main_tab)

        for i, combo_box in enumerate(self.combo_boxes):
            combo_box.activated.connect(self.crv_set)

        self.combo_boxes[1].setVisible(False)
        self.combo_boxes[2].setVisible(False)
        self.combo_boxes[3].setVisible(False)
        self.plot_widgets[1].setVisible(False)
        self.plot_widgets[2].setVisible(False)
        self.plot_widgets[3].setVisible(False)

        self.update_serial_port()
        self.update_time()
        self.load_data()
        # self.update_main_tab()
        self.is_running = False  
        self.viewTab.start_button.clicked.connect(self.handle_start)
        self.viewTab.stop_button.clicked.connect(self.handle_stop)

    def handle_start(self):
        if not self.is_running:
            self.start_program()
            self.is_running = True

    def handle_stop(self):
        if self.is_running:
            self.stop_program()
            self.is_running = False

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
        self.viewTab.com_port_combo.addItems([port.name for port in ports])
        self.viewTab.com_port_combo.activated.connect(self.update_serial_port)

    def select_time(self):
        self.sampling_rate = self.read_sf().get('value', 1) 
        
        selected_time = int(self.viewTab.seconds_combo.currentText())
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

    def update_time(self):
        self.time = [1, 5, 10]
        self.viewTab.seconds_combo.addItems([str(t) for t in self.time])

    def update_serial_port(self):
        self.serial_port = serial.Serial(self.viewTab.com_port_combo.currentText(), 115200)

    def toggle_record(self):
        if not self.recording:
            self.start_record()
        else:
            self.stop_record()
            
    def start_record(self):
        self.recording = True
        self.viewTab.record_button.setStyleSheet("background-color: red")
        self.csv_writer.writerow(["Time"] + list(self.parameters.keys()))

    def stop_record(self):
        self.recording = False
        self.viewTab.record_button.setStyleSheet("background-color: green")
        self.csv_file.close()  # Close the CSV file

    def change_color(self):
        self.toggle_record()

    def dynamic_widgets(self):
        self.combo_boxes = []
        self.plot_widgets = []

        y_limits = self.read_y_limits()
        print(y_limits) 

        for i in range(4):
            combo_box = QtWidgets.QComboBox()
            combo_box.setObjectName(f"combo_box_{i+1}")
            combo_box.addItems(self.parameters.keys())
            self.viewTab.verticalLayout.addWidget(combo_box)
            self.combo_boxes.append(combo_box)

            plot_widget = pg.PlotWidget()
            self.viewTab.verticalLayout.addWidget(plot_widget, stretch=1)
            plot_widget.setBackground('w')
            self.plot_widgets.append(plot_widget)

            if f'y{i+1}' in y_limits:
                plot_widget.setYRange(y_limits[f'y{i+1}'][0], y_limits[f'y{i+1}'][1])
            else:
                print(f"Y limits not found for index {i}")

        print("Dynamic widgets created successfully")  # Debug statement

    def manage_widgets(self):
        self.spin_value = self.viewTab.spinBox.value()
        for i in range(4):
            self.combo_boxes[i].setVisible(i < self.spin_value)
            self.plot_widgets[i].setVisible(i < self.spin_value)

    def create_curve(self, plot_widget, index):
        plot_widget.clear()
        colors = ['r', 'g', 'b', 'y']
        curve = plot_widget.plot(pen=pg.mkPen(color=colors[index], width=2.5), name=f"Parameter {index+1}")
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
                if selected_index < len(self.parameters):
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
                    progress_callback.emit(unpacked_data)
                    # print(unpacked_data)
                except struct.error as e:
                    print("Error unpacking data:", e)
            if self.trigger == 1:
                self.trigger = 2
                break
                    
    @pyqtSlot(list)
    def update_plot(self, data):
        if self.recording:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            record_data = [timestamp] + list(data)
            self.csv_writer.writerow(record_data)

        for i in range(self.spin_value):
            if self.combo_boxes[i].isVisible():
                selected_index = self.combo_boxes[i].currentIndex()
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

    def stop_program(self):
        self.recording = False
        # self.serial_port.close()
        # self.thread_complete()
        self.trigger = 1
        self.viewTab.stop_button.setEnabled(False)
        self.viewTab.start_button.setEnabled(True)


    def start_program(self):
        self.worker_thread = Worker(self.unpack_values)
        self.worker_thread.signals.progress.connect(self.update_plot)
        self.worker_thread.signals.finished.connect(self.thread_complete)
        self.worker_thread.signals.result.connect(self.thread_complete)

        self.threadpool.start(self.worker_thread)

        self.viewTab.start_button.setEnabled(False)
        self.viewTab.stop_button.setEnabled(True)
        

        
    def add_rows(self):
        self.settingsTab.tableWidget.insertRow(self.settingsTab.tableWidget.rowCount()-1)
        self.settingsTab.tableWidget.insertColumn(self.settingsTab.tableWidget.rowCount()-1)
        
    def load_data(self):
        config = toml.load('config.toml')
        parameters = config.get('parameters', {})

        self.settingsTab.tableWidget.setRowCount(len(parameters))
        self.settingsTab.tableWidget.setColumnCount(2)
        self.settingsTab.tableWidget.setHorizontalHeaderLabels(["Sensor ", "Data Type"])

        # Load sensor parameters
        for i, (sensor, datatype) in enumerate(parameters.items()):
            sensor_item = QTableWidgetItem(sensor)
            datatype_item = QTableWidgetItem(datatype)
            self.settingsTab.tableWidget.setItem(i, 0, sensor_item)
            self.settingsTab.tableWidget.setItem(i, 1, datatype_item)

        # Load y limits
        y_limits = config.get('y_limit', {})
        self.settingsTab.lineEdit.setText(str(y_limits.get('y1', [])[0]))
        self.settingsTab.lineEdit_2.setText(str(y_limits.get('y2', [])[0]))
        self.settingsTab.lineEdit_3.setText(str(y_limits.get('y3', [])[0]))
        self.settingsTab.lineEdit_4.setText(str(y_limits.get('y4', [])[0]))
        self.settingsTab.lineEdit_5.setText(str(y_limits.get('y1', [])[1]))
        self.settingsTab.lineEdit_6.setText(str(y_limits.get('y2', [])[1]))
        self.settingsTab.lineEdit_7.setText(str(y_limits.get('y3', [])[1]))
        self.settingsTab.lineEdit_8.setText(str(y_limits.get('y4', [])[1]))

        self.settingsTab.com_sf.setText(str(config.get('sampling_frequency', 1)))

    def save_data(self):
        config = toml.load('config.toml')
        parameters = {}

        for row in range(self.settingsTab.tableWidget.rowCount()):
            sensor_item = self.settingsTab.tableWidget.item(row, 0)
            datatype_item = self.settingsTab.tableWidget.item(row, 1)
            if sensor_item is not None and datatype_item is not None:
                sensor = sensor_item.text().lower()
                datatype = datatype_item.text().lower()
                parameters[sensor] = datatype

        config['parameters'] = parameters

        y_limits = {
            'y1': [float(self.settingsTab.lineEdit.text()), float(self.settingsTab.lineEdit_5.text())],
            'y2': [float(self.settingsTab.lineEdit_2.text()), float(self.settingsTab.lineEdit_6.text())],
            'y3': [float(self.settingsTab.lineEdit_3.text()), float(self.settingsTab.lineEdit_7.text())],
            'y4': [float(self.settingsTab.lineEdit_4.text()), float(self.settingsTab.lineEdit_8.text())]
        }
        config['y_limit'] = y_limits

        config['sampling_frequency'] = int(self.settingsTab.com_sf.text())

        with open('config.toml', 'w') as f:
            toml.dump(config, f)

        print("Data saved successfully!")
        print("Updated parameters:", parameters)

        self.update_plot_from_settings()

        self.update_main_tab()

    def thread_complete(self):
        print("THREAD COMPLETED!")

    def handle_error(self, error_tuple):
        print("ERROR:", error_tuple[0])

    def update_main_tab(self):
        config = self.read_config()
        y_limits = config.get('y_limit', {})
        parameters = config.get('parameters', {})

        self.curve_dict = {}

        for i, (plot_widget, combo_box) in enumerate(zip(self.plot_widgets[:4], self.combo_boxes[:4])):
            y_limit_key = f'y{i+1}'
            if y_limit_key in y_limits:
                plot_widget.setYRange(y_limits[y_limit_key][0], y_limits[y_limit_key][1])
            else:
                print(f"Y limit key {y_limit_key} not found in y_limits")

            combo_box.clear()
            combo_box.addItems(parameters.keys())

    def update_plot_from_settings(self):
    # Read the new y-axis limits from the settings
        y_limits = {
            'y1': [float(self.settingsTab.lineEdit.text()), float(self.settingsTab.lineEdit_5.text())],
            'y2': [float(self.settingsTab.lineEdit_2.text()), float(self.settingsTab.lineEdit_6.text())],
            'y3': [float(self.settingsTab.lineEdit_3.text()), float(self.settingsTab.lineEdit_7.text())],
            'y4': [float(self.settingsTab.lineEdit_4.text()), float(self.settingsTab.lineEdit_8.text())]
        }

        # Update the y-axis limits of the plot widgets
        for i, plot_widget in enumerate(self.plot_widgets):
            y_limit_key = f'y{i+1}'
            if y_limit_key in y_limits:
                y_min, y_max = y_limits[y_limit_key]
                plot_widget.setYRange(y_min, y_max)
            else:
                print(f"Y limit key {y_limit_key} not found in y_limits")

        # Read the new sampling frequency from the settings
        new_sf = int(self.settingsTab.com_sf.text())
        if new_sf != self.sampling_frequency:
            self.sampling_frequency = new_sf
            self.select_time()

        # Read the new sensor parameters from the settings
        parameters = {}
        for row in range(self.settingsTab.tableWidget.rowCount()):
            sensor_item = self.settingsTab.tableWidget.item(row, 0)
            datatype_item = self.settingsTab.tableWidget.item(row, 1)
            if sensor_item is not None and datatype_item is not None:
                sensor = sensor_item.text().lower()
                datatype = datatype_item.text().lower()
                parameters[sensor] = datatype

        if parameters != self.parameters:
            self.parameters = parameters
            self.load_data()
            self.crv_set()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
