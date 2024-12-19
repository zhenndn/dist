import sys
import re
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QInputDialog)
from PyQt5 import uic  # Для загрузки UI-файла


class FinanceManager(QMainWindow):
    def __init__(self):
        super().__init__()
        # Загружаем UI из файла
        uic.loadUi('finance_manager.ui', self)

        # Инициализация баланса и истории
        self.balance = 0.0
        self.income_history = []
        self.expense_history = []

        # Инициализация бюджета
        self.monthly_budget = 0.0  # Бюджет на месяц
        self.current_month_expenses = 0.0  # Траты текущего месяца

        # Устанавливаем стандартные категории
        self.income_categories = ["Зарплата", "Премия", "Подарок", "Другое"]
        self.expense_categories = ["Еда", "Транспорт", "Развлечения", "Коммунальные", "Другое"]

        # Загружаем категории в выпадающие списки
        self.comboBox.addItems(self.income_categories)
        self.comboBox_3.addItems(self.expense_categories)

        # Подключаем элементы интерфейса к методам
        self.pushButton.clicked.connect(self.add_income)  # Добавить доход
        self.pushButton_3.clicked.connect(self.add_expense)  # Добавить расход
        self.pushButton_4.clicked.connect(self.delete_history_entry)  # Удалить запись
        self.pushButton_5.clicked.connect(self.edit_history_entry)  # Редактировать запись
        self.pushButton_6.clicked.connect(self.set_monthly_budget)  # Установить бюджет на месяц

        # Устанавливаем начальный баланс
        self.update_balance()
        self.update_history()

    def is_valid_amount(self, amount_str):
        """Проверяет, является ли строка числом (целым или дробным)."""
        pattern = r'^\d+(\.\d+)?$'
        return bool(re.match(pattern, amount_str.replace(',', '.')))

    def set_monthly_budget(self):
        """Устанавливает бюджет на месяц."""
        budget_str, ok = QInputDialog.getText(self, "Установить бюджет", "Введите бюджет на месяц:")
        if ok and self.is_valid_amount(budget_str):
            self.monthly_budget = float(budget_str.replace(',', '.'))
            self.current_month_expenses = 0.0  # Сбрасываем текущие расходы
            QMessageBox.information(self, "Успех", f"Бюджет на месяц установлен: {self.monthly_budget:.2f} ₽")
            self.update_balance()
            self.update_history()

    def add_income(self):
        """Добавить доход."""
        try:
            amount_str = self.lineEdit.text()
            if not self.is_valid_amount(amount_str):
                raise ValueError("Некорректный формат суммы. Введите целое или дробное число.")
            amount = float(amount_str.replace(',', '.'))
            if amount <= 0:
                raise ValueError("Сумма дохода должна быть положительной.")
            category = self.comboBox.currentText()
            comment = self.lineEdit_2.text()

            # Обновляем баланс и историю
            self.balance += amount
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = f"Доход: {amount:.2f} ₽ ({category}, {current_time})"
            if comment:
                entry += f" - {comment}"
            self.income_history.append(entry)

            # Обновляем интерфейс
            self.update_balance()
            self.update_history()
            self.lineEdit.clear()
            self.lineEdit_2.clear()
        except ValueError as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_expense(self):
        """Добавить расход."""
        try:
            amount_str = self.lineEdit_5.text()
            if not self.is_valid_amount(amount_str):
                raise ValueError("Некорректный формат суммы. Введите целое или дробное число.")
            amount = float(amount_str.replace(',', '.'))
            if amount <= 0:
                raise ValueError("Сумма расхода должна быть положительной.")
            if amount > self.balance:
                raise ValueError("Расход превышает текущий баланс.")

            # Проверка превышения бюджета
            if self.monthly_budget > 0 and (self.current_month_expenses + amount) > self.monthly_budget:
                QMessageBox.warning(self, "Предупреждение", "Вы превысили бюджет на месяц!")

            category = self.comboBox_3.currentText()
            comment = self.lineEdit_6.text()

            # Обновляем баланс и историю
            self.balance -= amount
            self.current_month_expenses += amount
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = f"Расход: {amount:.2f} ₽ ({category}, {current_time})"
            if comment:
                entry += f" - {comment}"
            self.expense_history.append(entry)

            # Обновляем интерфейс
            self.update_balance()
            self.update_history()
            self.lineEdit_5.clear()
            self.lineEdit_6.clear()
        except ValueError as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def delete_history_entry(self):
        """Удалить запись из истории."""
        if not self.income_history and not self.expense_history:
            QMessageBox.information(self, "Информация", "Нет записей для удаления.")
            return

        # Составляем список всех записей
        history = self.income_history + self.expense_history
        items = [f"{i + 1}: {item}" for i, item in enumerate(history)]
        item_to_delete, ok = QInputDialog.getItem(self, "Удаление записи", "Выберите запись для удаления:", items, 0,
                                                  False)

        if ok and item_to_delete:
            index = int(item_to_delete.split(":")[0]) - 1
            if index < len(self.income_history):
                # Удаляем доход
                self.income_history.pop(index)
            else:
                # Удаляем расход
                index -= len(self.income_history)
                self.expense_history.pop(index)

            self.update_balance()
            self.update_history()

    def edit_history_entry(self):
        """Редактировать запись в истории."""
        if not self.income_history and not self.expense_history:
            QMessageBox.information(self, "Информация", "Нет записей для редактирования.")
            return

        # Составляем список всех записей
        history = self.income_history + self.expense_history
        items = [f"{i + 1}: {item}" for i, item in enumerate(history)]
        item_to_edit, ok = QInputDialog.getItem(self, "Редактирование записи", "Выберите запись для редактирования:",
                                                items, 0, False)

        if ok and item_to_edit:
            index = int(item_to_edit.split(":")[0]) - 1

            # Запрос новой суммы
            new_amount, ok_amount = QInputDialog.getText(self, "Новая сумма", "Введите новую сумму:")
            if ok_amount and self.is_valid_amount(new_amount):
                new_amount = float(new_amount.replace(',', '.'))

                # Редактируем запись
                if index < len(self.income_history):
                    self.income_history[index] = f"Доход: {new_amount:.2f} ₽ (отредактировано)"
                else:
                    index -= len(self.income_history)
                    self.expense_history[index] = f"Расход: {new_amount:.2f} ₽ (отредактировано)"

                self.update_history()
                self.update_balance()

    def update_balance(self):
        """Обновляет текст текущего баланса."""
        total_income = sum(float(item.split("₽")[0].split(":")[1].strip()) for item in self.income_history)
        total_expense = sum(float(item.split("₽")[0].split(":")[1].strip()) for item in self.expense_history)
        self.balance = total_income - total_expense
        self.label_10.setText(f"Общий баланс: {self.balance:.2f} ₽")

    def update_history(self):
        """Обновляет текстовую историю операций."""
        history = "История операций:\n"
        if self.income_history:
            history += "\n".join(self.income_history)
        history += "\n" + "-" * 50 + "\n"
        if self.expense_history:
            history += "\n".join(self.expense_history)
        history += "\n" + "-" * 50 + "\n"
        # Отчет о расходах за месяц
        if self.monthly_budget > 0:
            history += f"\nТраты за месяц: {self.current_month_expenses:.2f} ₽ из {self.monthly_budget:.2f} ₽ бюджета."
            if self.current_month_expenses > self.monthly_budget:
                history += "\nВнимание: Превышен бюджет месяца!"

        self.textEdit.setText(history)
if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = FinanceManager()
        window.show()
        sys.exit(app.exec_())