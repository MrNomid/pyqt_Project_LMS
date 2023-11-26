from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt5 import uic
from PyQt5.QtCore import Qt

import sqlite3


class DBSelectionWidget(QMainWindow):  # Просмотр БД
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('forms/CheckKonsForm.ui', self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Просмотр Ребёнка')
        self.deleteButton.clicked.connect(self.deleting)
        self.printing()
        self.findButton.clicked.connect(self.printing)
        self.checkButton.clicked.connect(self.info_showing)
        self.tableWidget.horizontalHeader().resizeSection(2, 0)
        self.tableWidget.horizontalHeader().resizeSection(1, 70)
        self.tableWidget.selectionModel().selectionChanged.connect(self.on_selection_changet)
        self.back_button.clicked.connect(self.back)

    def printing(self):  # Вывод данных из БД
        self.tableWidget.setRowCount(0)
        # Проверка на наличие текста в поисковой строке
        if self.childName.text():
            con = sqlite3.connect('database.sql')
            cur = con.cursor()
            res = cur.execute("""SELECT id, Child_Name, Kons_Date from form WHERE Child_Name LIKE ?""",
                              (f'{self.childName.text()}%', )).fetchall()

        else:
            con = sqlite3.connect('database.sql')
            cur = con.cursor()
            res = cur.execute("""SELECT id, Child_Name, Kons_Date from form""").fetchall()
            res = sorted(res, key=lambda x: x[1])

        for line in res:  # Добавление данных в TableWidget
            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)
            self.tableWidget.setItem(rowPosition, 2, QTableWidgetItem(str(line[0])))
            self.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(str(line[1])))
            self.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(str(line[2])))

    def on_selection_changet(self, selected):  # При выборе строки в TableWidget

        for index in selected.indexes():
            self.current_id = self.tableWidget.item(index.row(), 2).text()

    def deleting(self):  # Удаление выбранной консультации из БД

        con = sqlite3.connect('database.sql')
        cur = con.cursor()
        res = cur.execute("""DELETE from form where id = ?""", (int(self.current_id), ))

        con.commit()

        self.printing()

    def info_showing(self):  # Показать информацию о выбранной консультации
        from ShowInfo import ShowInfoWidget

        self.hide()
        self.add_form = ShowInfoWidget(self, self.current_id)
        self.add_form.show()

    def back(self):
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:  # Активация кнопки "Найти" при нажатии Enter
            self.printing()

        elif event.key() == Qt.Key_Escape:  # Выход при нажатии Esc
            self.back()
