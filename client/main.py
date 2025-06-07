from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QListWidget,
    QLabel, QLineEdit, QMessageBox, QHBoxLayout, QGridLayout, QListWidgetItem,
    QToolBar, QTableWidget, QTableWidgetItem, QComboBox, QDialog, QFormLayout, QDialogButtonBox
)
from PyQt5.QtCore import Qt
import api

class AddProductDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добави нов продукт")
        layout = QFormLayout()

        self.name_input = QLineEdit()
        self.barcode_input = QLineEdit()
        self.quantity_input = QLineEdit("0")
        self.price_input = QLineEdit("0.0")

        layout.addRow("Име:", self.name_input)
        layout.addRow("Баркод:", self.barcode_input)
        layout.addRow("Количество:", self.quantity_input)
        layout.addRow("Цена:", self.price_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "barcode": self.barcode_input.text(),
            "quantity": int(self.quantity_input.text()),
            "price": float(self.price_input.text())
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZdravSoft - Продажби")
        self.setGeometry(100, 100, 800, 600)

        toolbar = QToolBar("Основно меню")
        self.addToolBar(toolbar)

        warehouse_btn = QPushButton("Склад")
        warehouse_btn.clicked.connect(self.open_warehouse_window)
        toolbar.addWidget(warehouse_btn)

        settings_btn = QPushButton("Настройки")
        settings_btn.clicked.connect(self.open_settings_window)
        toolbar.addWidget(settings_btn)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Въведи баркод или номер и натисни Enter")
        self.search_input.returnPressed.connect(self.scan_product)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        quick_layout = QGridLayout()
        self.quick_buttons = []
        for i in range(9):
            btn = QPushButton(f"Бърз бутон {i+1}")
            btn.clicked.connect(lambda _, idx=i: self.add_quick_product(idx))
            self.quick_buttons.append(btn)
            quick_layout.addWidget(btn, i // 3, i % 3)
        layout.addLayout(quick_layout)

        qty_layout = QHBoxLayout()
        qty_layout.addWidget(QLabel("Количество:"))
        self.qty_input = QLineEdit("1")
        qty_layout.addWidget(self.qty_input)
        layout.addLayout(qty_layout)

        layout.addWidget(QLabel("Текуща продажба:"))
        self.receipt_list = QListWidget()
        self.receipt_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.receipt_list.customContextMenuRequested.connect(self.remove_product)
        layout.addWidget(self.receipt_list)

        self.total_label = QLabel("Обща сума: 0 лв.")
        layout.addWidget(self.total_label)

        finish_btn = QPushButton("Завърши продажба")
        finish_btn.clicked.connect(self.finish_sale)
        layout.addWidget(finish_btn)

        central_widget.setLayout(layout)

    def scan_product(self):
        barcode = self.search_input.text().strip()
        if not barcode:
            return
        products = api.get_products()
        for p in products:
            if barcode == str(p['id']) or barcode == p['barcode']:
                try:
                    qty = int(self.qty_input.text()) if self.qty_input.text() else 1
                except ValueError:
                    qty = 1
                self.add_product_to_receipt(p['id'], p['name'], qty, p['price'])
                self.qty_input.setText("1")
                self.search_input.clear()
                break
        else:
            QMessageBox.warning(self, "Грешка", "Продуктът не е намерен!")

    def add_quick_product(self, idx):
        if idx < len(api.quick_buttons):
            product_id = api.quick_buttons[idx]
            product = api.get_product(product_id)
            if product:
                try:
                    qty = int(self.qty_input.text()) if self.qty_input.text() else 1
                except ValueError:
                    qty = 1
                self.add_product_to_receipt(product['id'], product['name'], qty, product['price'])
                self.qty_input.setText("1")

    def add_product_to_receipt(self, product_id, name, qty, price):
        item_text = f"{name} x{qty} - {price*qty} лв."
        item = QListWidgetItem(item_text)
        item.setData(Qt.UserRole, {"product_id": product_id, "quantity": qty, "price": price})
        self.receipt_list.addItem(item)
        self.update_total()

    def remove_product(self, pos):
        item = self.receipt_list.itemAt(pos)
        if item:
            self.receipt_list.takeItem(self.receipt_list.row(item))
            self.update_total()

    def update_total(self):
        total = 0
        for i in range(self.receipt_list.count()):
            data = self.receipt_list.item(i).data(Qt.UserRole)
            total += data["quantity"] * data["price"]
        self.total_label.setText(f"Обща сума: {total} лв.")

    def finish_sale(self):
        if self.receipt_list.count() == 0:
            QMessageBox.warning(self, "Грешка", "Няма продукти!")
            return
        items = []
        total = 0
        for i in range(self.receipt_list.count()):
            data = self.receipt_list.item(i).data(Qt.UserRole)
            items.append(data)
            total += data["quantity"] * data["price"]
        sale_data = {"total_amount": total, "items": items}
        response = api.create_sale(sale_data)
        QMessageBox.information(self, "Успех", f"Продажбата е записана (ID: {response['id']})")
        self.receipt_list.clear()
        self.update_total()

    def open_warehouse_window(self):
        self.warehouse_window = WarehouseWindow()
        self.warehouse_window.show()

    def open_settings_window(self):
        self.settings_window = SettingsWindow()
        self.settings_window.show()

class WarehouseWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Склад - Продукти")
        self.setGeometry(150, 150, 600, 400)
        layout = QVBoxLayout()

        add_btn = QPushButton("Добави нов продукт")
        add_btn.clicked.connect(self.add_new_row)
        layout.addWidget(add_btn)

        save_btn = QPushButton("Запази промените")
        save_btn.clicked.connect(self.save_changes)
        layout.addWidget(save_btn)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Име", "Баркод", "Количество", "Цена"])
        self.table.setEditTriggers(QTableWidget.AllEditTriggers)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_products()

    def load_products(self):
        products = api.get_products()
        self.table.setRowCount(len(products))
        for row, product in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(str(product["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(product["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(product["barcode"]))
            self.table.setItem(row, 3, QTableWidgetItem(str(product["quantity"])))
            self.table.setItem(row, 4, QTableWidgetItem(str(product["price"])))

    def add_new_row(self):
        dialog = AddProductDialog()
        if dialog.exec_() == QDialog.Accepted:
            product_data = dialog.get_data()
            response = api.add_product(product_data)
            if response and "id" in response:
                new_id = response["id"]
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(new_id)))
                self.table.setItem(row, 1, QTableWidgetItem(product_data["name"]))
                self.table.setItem(row, 2, QTableWidgetItem(product_data["barcode"]))
                self.table.setItem(row, 3, QTableWidgetItem(str(product_data["quantity"])))
                self.table.setItem(row, 4, QTableWidgetItem(str(product_data["price"])))
                QMessageBox.information(self, "Успех", "Продуктът е добавен!")
            else:
                QMessageBox.warning(self, "Грешка", "Неуспешно добавяне!")

    def save_changes(self):
        for row in range(self.table.rowCount()):
            id_item = self.table.item(row, 0)
            product_id = int(id_item.text()) if id_item and id_item.text().isdigit() else None
            name = self.table.item(row, 1).text()
            barcode = self.table.item(row, 2).text()
            quantity = int(self.table.item(row, 3).text())
            price = float(self.table.item(row, 4).text())

            product_data = {"name": name, "barcode": barcode, "quantity": quantity, "price": price}

            if product_id:
                api.update_product(product_id, product_data)
            else:
                api.add_product(product_data)
        QMessageBox.information(self, "Успех", "Промените са запазени!")
        self.load_products()

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройки - Бързи бутони")
        self.setGeometry(200, 200, 400, 400)
        layout = QVBoxLayout()
        self.combo_boxes = []
        products = api.get_products()
        for i in range(9):
            cb = QComboBox()
            cb.addItem("Не е зададен")
            for p in products:
                cb.addItem(f"{p['id']} - {p['name']}", p["id"])
            self.combo_boxes.append(cb)
            layout.addWidget(QLabel(f"Бутон {i+1}:"))
            layout.addWidget(cb)
        save_btn = QPushButton("Запази настройките")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def save_settings(self):
        ids = []
        for cb in self.combo_boxes:
            product_id = cb.currentData()
            ids.append(product_id if product_id else None)
        api.save_quick_buttons(ids)
        QMessageBox.information(self, "Успех", "Настройките са запазени!")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
