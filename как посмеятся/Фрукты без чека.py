import sys
from PyQt6 import QtWidgets, QtGui, QtCore

class Product:
    def __init__(self, name: str, price: float, category: str, image_path: str = ""):
        self.name = name
        self.price = price
        self.category = category
        self.image_path = image_path

    def __repr__(self):
        return f"{self.name} ({self.price} руб)"

class ShoppingCart:
    def __init__(self):
        self.items = {}  # {product: quantity}

    def add_product(self, product: Product, quantity: int):
        if product in self.items:
            self.items[product] += quantity
        else:
            self.items[product] = quantity

    def remove_product(self, product: Product):
        if product in self.items:
            del self.items[product]

    def get_total_cost(self) -> float:
        total = sum(product.price * qty for product, qty in self.items.items())
        return round(total, 2)

    def clear(self):
        self.items.clear()

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛒 Магазин продуктов и масок")
        self.resize(1000, 800)
        self.setStyleSheet("""
            QWidget {
                background-color: #6A5ACD;
                color: #FFFFFF;
                font-family: Arial;
            }
            QTabWidget::pane {
                border: 2px solid #FFFFFF;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #9370DB;
                padding: 8px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background: #BA55D3;
            }
            QPushButton {
                background-color: #9370DB;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #BA55D3;
            }
            QLabel {
                font-size: 16px;
            }
            QTableWidget {
                background-color: #8A2BE2;
                color: #FFFFFF;
                gridline-color: #FFFFFF;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #FFFFFF;
                color: #000000;
                border-radius: 4px;
                padding: 4px;
            }
        """)

        # Все товары с категориями и изображениями (путь к картинкам при необходимости)
        self.products = [
            Product("Яблоки 1кг", 90, "Фрукты"),
            Product("Бананы 1кг", 120, "Фрукты"),
            Product("Помидоры 1кг", 80, "Овощи"),
            Product("Огурцы 1кг", 70, "Овощи"),
            Product("Молоко 1л", 80, "Другое"),
            Product("Хлеб батон", 50, "Другое"),
            Product("Маска Мистер Бист", 100, "Маски"),
            Product("Маска Спайдермен", 150, "Маски"),
            Product("Котик с усами", 50, "Смешное"),
        ]

        self.cart = ShoppingCart()

        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        # Вкладки по категориям
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabPosition(QtWidgets.QTabWidget.TabPosition.North)
        self.tabs.setMovable(False)

        categories = ["Фрукты", "Овощи", "Маски", "Другое", "Смешное"]
        self.category_tabs = {}

        for cat in categories:
            tab = QtWidgets.QWidget()
            self.setup_category_tab(tab, cat)
            self.tabs.addTab(tab, cat)
            self.category_tabs[cat] = tab

        main_layout.addWidget(self.tabs)

        # Ваша корзина
        self.cart_group = QtWidgets.QGroupBox("Ваша корзина")
        self.cart_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        self.cart_layout = QtWidgets.QVBoxLayout()

        self.cart_table = QtWidgets.QTableWidget()
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(["Товар", "Цена", "Кол-во", "Сумма"])
        self.cart_table.verticalHeader().setVisible(False)
        self.cart_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.cart_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.cart_table.setFixedHeight(350)
        self.cart_table.resizeColumnsToContents()
        self.cart_layout.addWidget(self.cart_table)

        # Итог и кнопки
        bottom_hlayout = QtWidgets.QHBoxLayout()
        self.total_label = QtWidgets.QLabel("Итого: 0.00 руб")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 18px;")
        bottom_hlayout.addWidget(self.total_label)

        self.clear_btn = QtWidgets.QPushButton("🗑️ Очистить корзину")
        self.clear_btn.clicked.connect(self.clear_cart)

        self.order_btn = QtWidgets.QPushButton("✅ Оформить заказ")
        self.order_btn.clicked.connect(self.checkout)

        bottom_hlayout.addWidget(self.clear_btn)
        bottom_hlayout.addWidget(self.order_btn)

        # Способ оплаты
        self.payment_method_box = QtWidgets.QGroupBox("Способ оплаты")
        self.payment_method_box.setStyleSheet("QGroupBox { font-size: 14px; }")
        payment_layout = QtWidgets.QHBoxLayout()

        self.cash_radio = QtWidgets.QRadioButton("Наличными")
        self.cash_radio.setChecked(True)
        self.card_radio = QtWidgets.QRadioButton("Картой")
        self.card_radio.toggled.connect(self.toggle_payment_fields)

        payment_layout.addWidget(self.cash_radio)
        payment_layout.addWidget(self.card_radio)

        # Поле для номера карты
        self.card_number_input = QtWidgets.QLineEdit()
        self.card_number_input.setPlaceholderText("Введите номер карты")
        self.card_number_input.setEnabled(False)
        payment_layout.addWidget(self.card_number_input)

        self.payment_method_box.setLayout(payment_layout)

        self.cart_layout.addWidget(self.payment_method_box)
        self.cart_layout.addLayout(bottom_hlayout)

        self.cart_group.setLayout(self.cart_layout)
        main_layout.addWidget(self.cart_group)

        self.update_cart_display()

    def setup_category_tab(self, tab, category):
        layout = QtWidgets.QVBoxLayout()
        # Таблица товаров
        table = QtWidgets.QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Товар", "Цена"])
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        # Заполняем товары по категории
        filtered = [p for p in self.products if p.category == category]
        table.setRowCount(0)
        for product in filtered:
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QtWidgets.QTableWidgetItem(product.name))
            table.setItem(row, 1, QtWidgets.QTableWidgetItem(f"{product.price} руб"))
        table.resizeColumnsToContents()
        table.setFixedHeight(200)
        layout.addWidget(table)

        # Кнопка добавления
        btn = QtWidgets.QPushButton("➕ Добавить в корзину")
        btn.clicked.connect(lambda: self.add_product_from_table(table))
        layout.addWidget(btn, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

        # Передача таблицы для дальнейших действий
        tab.layout = layout
        tab.table = table

        tab.setLayout(layout)

    def add_product_from_table(self, table):
        selected_rows = table.selectionModel().selectedRows()
        if not selected_rows:
            QtWidgets.QMessageBox.warning(self, "Внимание", "Пожалуйста, выберите товар.")
            return
        row = selected_rows[0].row()
        name = table.item(row, 0).text()
        price = float(table.item(row, 1).text().replace(" руб", ""))
        product = next(p for p in self.products if p.name == name and p.price == price)
        qty, ok = QtWidgets.QInputDialog.getInt(self, "Количество", f"Введите количество {name}:", min=1, max=100)
        if ok:
            self.cart.add_product(product, qty)
            self.update_cart_display()

    def buy_special_mask(self, mask_name):
        product = next(p for p in self.products if p.name == mask_name)
        self.cart.add_product(product, 1)
        self.update_cart_display()

    def update_cart_display(self):
        self.cart_table.setRowCount(0)
        for product, qty in self.cart.items.items():
            total = product.price * qty
            row = self.cart_table.rowCount()
            self.cart_table.insertRow(row)
            self.cart_table.setItem(row, 0, QtWidgets.QTableWidgetItem(product.name))
            self.cart_table.setItem(row, 1, QtWidgets.QTableWidgetItem(f"{product.price} руб"))
            self.cart_table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(qty)))
            self.cart_table.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{total:.2f} руб"))
        total_cost = self.cart.get_total_cost()
        self.total_label.setText(f"Итого: {total_cost:.2f} руб")

    def clear_cart(self):
        reply = QtWidgets.QMessageBox.question(self, "Подтверждение", "Очистить всю корзину?", QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.cart.clear()
            self.update_cart_display()

    def checkout(self):
        if not self.cart.items:
            QtWidgets.QMessageBox.information(self, "Корзина пуста", "Добавьте товары перед оформлением.")
            return
        total = self.cart.get_total_cost()
        payment_method = "Наличными" if self.cash_radio.isChecked() else "Картой"
        if payment_method == "Картой":
            card_number = self.card_number_input.text()
            if not card_number:
                QtWidgets.QMessageBox.warning(self, "Внимание", "Пожалуйста, введите номер карты.")
                return
        reply = QtWidgets.QMessageBox.question(self, "Оформление заказа", f"Подтвердить заказ на {total:.2f} руб через {payment_method}?", QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.show_receipt()
            self.cart.clear()
            self.update_cart_display()

    def toggle_payment_fields(self):
        self.card_number_input.setEnabled(self.card_radio.isChecked())

    def show_receipt(self):
        total = self.cart.get_total_cost()
        # Создаем окно с чеком и фото товара
        receipt_window = QtWidgets.QWidget()
        receipt_window.setWindowTitle("🧾 Ваш чек")
        receipt_window.resize(600, 400)
        receipt_window.setStyleSheet("background-color: #F5F5DC; font-family: Arial;")
        layout = QtWidgets.QVBoxLayout()

        # Заголовок
        title = QtWidgets.QLabel("🧾 Спасибо за покупку!")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #8B0000;")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Фото товара (если есть)
        if self.cart.items:
            # берем изображение первого товара
            first_product = next(iter(self.cart.items))
            img_path = first_product.image_path
            if img_path:
                pixmap = QtGui.QPixmap(img_path).scaled(150, 150, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
                img_label = QtWidgets.QLabel()
                img_label.setPixmap(pixmap)
                img_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(img_label)

        # Таблица с купленными товарами
        table = QtWidgets.QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Товар", "Кол-во", "Цена"])
        table.verticalHeader().setVisible(False)
        for product, qty in self.cart.items.items():
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QtWidgets.QTableWidgetItem(product.name))
            table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(qty)))
            table.setItem(row, 2, QtWidgets.QTableWidgetItem(f"{product.price} руб"))
        table.resizeColumnsToContents()
        layout.addWidget(table)

        # Итоговая сумма
        total_label = QtWidgets.QLabel(f"Общая сумма: {total:.2f} руб")
        total_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #006400;")
        total_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(total_label)

        # QR-код или изображение (можно вставить изображение чека)
        # Для примера добавим просто текст или изображение
        check_image_path = ""  # путь к изображению чека
        # если есть изображение, можно вставить
        # например, если у вас есть файл "check.png"
        # check_image_path = "check.png"
        # if check_image_path:
        #     pixmap_check = QtGui.QPixmap(check_image_path).scaled(200, 100, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        #     check_label = QtWidgets.QLabel()
        #     check_label.setPixmap(pixmap_check)
        #     check_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        #     layout.addWidget(check_label)

        # Кнопка закрытия
        close_btn = QtWidgets.QPushButton("Закрыть")
        close_btn.clicked.connect(receipt_window.close)
        layout.addWidget(close_btn, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        receipt_window.setLayout(layout)
        receipt_window.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())