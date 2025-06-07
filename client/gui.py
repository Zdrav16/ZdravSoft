from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QListWidget,
    QLabel, QLineEdit, QMessageBox, QHBoxLayout, QGridLayout, QListWidgetItem
)
from PyQt5.QtGui import QFont
import api

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZdravSoft - Продажби")
        self.setGeometry(100, 100, 800, 600)

        # Зареждаме стиловете
        with open("styles.qss", "r") as f:
            self.setStyleSheet(f.read())

        # Основен widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Бутон за добавяне на стока (отваря диалог)
        add_stock_btn = QPushButton("Добави нова стока")
        add_stock_btn.clicked.connect(self.add_product_dialog)
        layout.addWidget(add_stock_btn)

        # Поле за търсене
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Търси по име, баркод или ID")
        search_btn = QPushButton("Търси")
        search_btn.clicked.connect(self.search_product)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)

        # Бързи бутони (примерно 9)
        quick_buttons_layout = QGridLayout()
        self.quick_buttons = []
        for i in range(9):
            btn = QPushButton(f"Бутон {i+1}")
            btn.clicked.connect(lambda _, idx=i: self.add_quick_product(idx))
            self.quick_buttons.append(btn)
            quick_buttons_layout.addWidget(btn, i // 3, i % 3)
        layout.addLayout(quick_buttons_layout)

        # „Касова бележка“ – списък с добавени продукти
        layout.addWidget(QLabel("Текуща продажба:"))
        self.receipt_list = QListWidget()
        layout.addWidget(self.receipt_list)

        # Бутон за завършване
        finish_btn = QPushButton("Завърши продажба")
        finish_btn.clicked.connect(self.finish_sale)
        layout.addWidget(finish_btn)

        central_widget.setLayout(layout)

        # Данни за текущата продажба
        self.sale_items = []

    def add_product_dialog(self):
        # Тук ще отворим нов прозорец за въвеждане на нова стока (по-късно)
        pass

    def search_product(self):
        # Логика за търсене по име, баркод или ID
        term = self.search_input.text()
        products = api.get_products()
        for p in products:
            if term in str(p['id']) or term in p['name'] or term in p['barcode']:
                self.add_product_to_receipt(p['id'], p['name'], 1, 1.0)

    def add_quick_product(self, idx):
        # Пример: всеки бутон е свързан с фиксиран продукт
        # Тук можеш да настроиш какво да добавя
        products = api.get_products()
        if idx < len(products):
            p = products[idx]
            self.add_product_to_receipt(p['id'], p['name'], 1, 1.0)

    def add_product_to_receipt(self, product_id, name, qty, price):
        item_text = f"{name} x{qty} - {price*qty} лв."
        item = QListWidgetItem(item_text)
        item.setData(1000, {"product_id": product_id, "quantity": qty, "price": price})
        self.receipt_list.addItem(item)

        # Десен бутон за изтриване
        item.setFlags(item.flags() | Qt.ItemIsSelectable)
        item.setToolTip("Десен клик за изтриване")
        self.receipt_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.receipt_list.customContextMenuRequested.connect(self.remove_product)

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
            data = self.receipt_list.item(i).data(1000)
            items.append(data)
            total += data["quantity"] * data["price"]

        sale_data = {"total_amount": total, "items": items}
        response = api.create_sale(sale_data)
        QMessageBox.information(self, "Успех", f"Продажбата е записана (ID: {response['id']})")
        self.receipt_list.clear()
