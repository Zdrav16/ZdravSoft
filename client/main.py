from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit,
    QMessageBox, QHBoxLayout, QGridLayout, QListWidget, QListWidgetItem, QToolBar,
    QTableWidget, QTableWidgetItem, QComboBox, QDialog, QFormLayout, QDialogButtonBox
)
from PyQt5.QtCore import Qt
import api
import sys

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
        self.setWindowTitle("POS System")
        self.setGeometry(100, 100, 1200, 800)

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Sidebar (по-компактен)
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(80)  # по-тесен Sidebar
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setAlignment(Qt.AlignTop)
        for name in ["POS", "History", "Customers", "Analytics"]:
            btn = QPushButton(name)
            btn.setFixedHeight(40)  # по-малки бутони
            btn.setStyleSheet("font-size: 10px;")  # по-малък шрифт
            sidebar_layout.addWidget(btn)
        main_layout.addWidget(sidebar_widget)

        # Products Area (ще заема повече място)
        products_area = QVBoxLayout()
        self.products_layout = QGridLayout()
        self.products_layout.setSpacing(10)
        products_area.addLayout(self.products_layout)
        main_layout.addLayout(products_area, 6)  # по-голямо тегло (4 вместо 3)

        # Order Panel (остава същото)
        order_panel = QVBoxLayout()
        order_panel.addWidget(QLabel("<b>Current Order</b>"))
        self.order_list = QListWidget()
        order_panel.addWidget(self.order_list)
        self.total_label = QLabel("Total: $0.00")
        order_panel.addWidget(self.total_label)
        charge_btn = QPushButton("Charge")
        charge_btn.clicked.connect(self.finish_sale)
        order_panel.addWidget(charge_btn)
        main_layout.addLayout(order_panel, 1)

        self.setCentralWidget(main_widget)
        self.load_products()


        # Автоматично зареждаме продуктите при стартиране
        self.load_products()

    def load_products(self):
        products = api.get_products()
        for i, p in enumerate(products):
            widget = QWidget()
            widget.setFixedSize(120, 100)  # по-малък контейнер
            layout = QVBoxLayout(widget)
            layout.setSpacing(3)  # по-малко разстояние вътре
            layout.addWidget(QLabel(f"<b>{p['name']}</b>"))
            layout.addWidget(QLabel(f"Цена: {p['price']}"))
            btn = QPushButton("Add to Cart")
            btn.setFixedSize(100, 30)
            btn.clicked.connect(lambda _, p=p: self.add_to_cart(p))
            layout.addWidget(btn)
            row, col = divmod(i, 3)
            self.products_layout.addWidget(widget, row, col)

    def add_to_cart(self, product):
        qty, ok = QLineEdit.getText(self, "Количество", f"Въведи количество за {product['name']}:", QLineEdit.Normal, "1")
        if not ok:
            return
        try:
            qty = int(qty)
        except ValueError:
            qty = 1
        item_text = f"{product['name']} x{qty} - {product['price']*qty} лв."
        item = QListWidgetItem(item_text)
        item.setData(Qt.UserRole, {"product_id": product["id"], "quantity": qty, "price": product["price"]})
        self.order_list.addItem(item)
        self.update_total()

    def update_total(self):
        total = 0
        for i in range(self.order_list.count()):
            data = self.order_list.item(i).data(Qt.UserRole)
            total += data["quantity"] * data["price"]
        self.total_label.setText(f"Total: {total} лв.")

    def finish_sale(self):
        if self.order_list.count() == 0:
            QMessageBox.warning(self, "Грешка", "Няма продукти!")
            return
        products = {p["id"]: p for p in api.get_products()}
        for i in range(self.order_list.count()):
            data = self.order_list.item(i).data(Qt.UserRole)
            product = products.get(data["product_id"])
            if not product:
                QMessageBox.warning(self, "Грешка", f"Продукт с ID {data['product_id']} не е намерен!")
                return
            if data["quantity"] > product["quantity"]:
                QMessageBox.warning(
                    self, "Недостатъчни наличности!",
                    f"Недостатъчно количество за {product['name']} (наличност: {product['quantity']})"
                )
                return
        items = []
        total = 0
        for i in range(self.order_list.count()):
            data = self.order_list.item(i).data(Qt.UserRole)
            items.append(data)
            total += data["quantity"] * data["price"]
        sale_data = {"total_amount": total, "items": items}
        response = api.create_sale(sale_data)
        QMessageBox.information(self, "Успех", f"Продажбата е записана (ID: {response['id']})")
        self.order_list.clear()
        self.update_total()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
