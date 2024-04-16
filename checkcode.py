from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Table Widget Example")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(5)
        self.table_widget.setColumnCount(3)
        self.layout.addWidget(self.table_widget)

        self.table_widget.itemSelectionChanged.connect(self.on_selection_changed)
        self.table_widget.itemChanged.connect(self.on_item_changed)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Backspace:
            self.delete_selected_items()

    def delete_selected_items(self):
        selected_items = self.table_widget.selectedItems()
        rows = set()
        columns = set()

        for item in selected_items:
            rows.add(item.row())
            columns.add(item.column())

        for row in sorted(rows, reverse=True):
            self.table_widget.removeRow(row)

        for column in sorted(columns, reverse=True):
            self.table_widget.removeColumn(column)

    def on_selection_changed(self):
        selected_items = self.table_widget.selectedItems()
        if len(selected_items) > 0:
            print("Selection changed:", selected_items[0].text())

    def on_item_changed(self, item):
        print(f"Item changed: row={item.row()}, column={item.column()}, value={item.text()}")

if __name__ == "__main__":
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()