from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QListWidget,
    QLabel, QLineEdit, QMessageBox, QHBoxLayout, QGridLayout, QListWidgetItem, QInputDialog
)
from PyQt5.QtCore import Qt
import api

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZdravSoft - Продажби")
        self.setGeometry(100, 100, 800, 600)

        # Основен widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Поле за търсене
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Търси по име, баркод или ID")
        search_btn = QPushButton("Търси")
        search_btn.clicked.connect(self.search_product)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)

        # Бързи бутони
        quick_layout = QGridLayout()
        self.quick_buttons = []
        for i in range(9):
            btn = QPushButton(f"Бърз бутон {i+1}")
            btn.clicked.connect(lambda _, idx=i: self.add_quick_product(idx))
            self.quick_buttons.append(btn)
            quick_layout.addWidget(btn, i // 3, i % 3)
        layout.addLayout(quick_layout)

        # Списък с продукти
        layout.addWidget(QLabel("Налични продукти:"))
        self.product_list = QListWidget()
        layout.addWidget(self.product_list)

        # Поле за количество
        qty_layout = QHBoxLayout()
        qty_layout.addWidget(QLabel("Количество:"))
        self.qty_input = QLineEdit()
        qty_layout.addWidget(self.qty_input)
        layout.addLayout(qty_layout)

        # Касов бон
        layout.addWidget(QLabel("Текуща продажба:"))
        self.receipt_list = QListWidget()
        self.receipt_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.receipt_list.customContextMenuRequested.connect(self.remove_product)
        layout.addWidget(self.receipt_list)

        # Бутон за зареждане на продукти
        load_btn = QPushButton("Зареди продукти")
        load_btn.clicked.connect(self.load_products)
        layout.addWidget(load_btn)

        # Бутон за добавяне на нова стока
        add_product_btn = QPushButton("Добави нов продукт")
        add_product_btn.clicked.connect(self.add_product_dialog)
        layout.addWidget(add_product_btn)

        # Бутон за завършване
        finish_btn = QPushButton("Завърши продажба")
        finish_btn.clicked.connect(self.finish_sale)
        layout.addWidget(finish_btn)

        central_widget.setLayout(layout)

        self.sale_items = []

    def load_products(self):
        self.product_list.clear()
        products = api.get_products()
        for p in products:
            self.product_list.addItem(f"{p['id']} - {p['name']} (наличност: {p['quantity']})")

    def search_product(self):
        term = self.search_input.text().lower()
        products = api.get_products()
        self.product_list.clear()
        for p in products:
            if term in str(p['id']) or term in p['name'].lower() or term in p['barcode']:
                self.product_list.addItem(f"{p['id']} - {p['name']} (наличност: {p['quantity']})")

    def add_quick_product(self, idx):
        products = api.get_products()
        if idx < len(products):
            p = products[idx]
            self.add_product_to_receipt(p['id'], p['name'], 1, 1.0)  # фиксирана цена за тест

    def add_product_to_receipt(self, product_id, name, qty, price):
        item_text = f"{name} x{qty} - {price*qty} лв."
        item = QListWidgetItem(item_text)
        item.setData(Qt.UserRole, {"product_id": product_id, "quantity": qty, "price": price})
        self.receipt_list.addItem(item)

    def remove_product(self, pos):
        item = self.receipt_list.itemAt(pos)
        if item:
            self.receipt_list.takeItem(self.receipt_list.row(item))

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

    def add_product_dialog(self):
        name, ok1 = QInputDialog.getText(self, "Име на продукта", "Въведи име:")
        if not ok1 or not name:
            return
        barcode, ok2 = QInputDialog.getText(self, "Баркод", "Въведи баркод:")
        if not ok2 or not barcode:
            return
        qty, ok3 = QInputDialog.getInt(self, "Количество", "Въведи количество:", 1, 1, 1000, 1)
        if not ok3:
            return

        product_data = {"name": name, "barcode": barcode, "quantity": qty}
        response = api.add_product(product_data)
        QMessageBox.information(self, "Добавено", f"Продуктът е добавен:\n{response}")
        self.load_products()
