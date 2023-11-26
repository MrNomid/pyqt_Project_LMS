from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

import os
import sqlite3

from AddKonsForm import AddKonsFormWidget
from DBSelection import DBSelectionWidget


class ShowInfoWidget(QMainWindow):  # Вывод подробной информации о конссультации из БД
    def __init__(self, parent=None, child=None):
        super().__init__(parent)
        uic.loadUi('forms/InfoKons.ui', self)
        self.child_id = child
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Информация о Ребёнке')
        self.showAgreementBtn.clicked.connect(self.agreement_showing_funk)
        self.editButton.clicked.connect(self.edit_funk)
        self.OKButton.clicked.connect(self.return_back)
        self.make_info()

    def make_info(self):  # Заполнение полей
        con = sqlite3.connect('database.sql')
        cur = con.cursor()
        res = cur.execute("""SELECT * from form WHERE id = ?""", (self.child_id, )).fetchall()

        self.perantName.setText(res[0][1])
        self.childBothDay.setText(res[0][3])
        self.perantAsk.setText(res[0][5])
        self.konsTheam.setText(cur.execute("""SELECT name from KonsTheams WHERE id = ?""",
                                           (res[0][6], )).fetchall()[0][0])
        self.KonsDate.setText(res[0][8])
        self.childName.setText(res[0][2])

        dou_visit = 'посещает ДОУ' if res[0][4] == 1 else 'не посещает ДОУ'
        konsul = 'первичная' if res[0][7] == 1 else 'повторная'
        self.moreInfo.setText(f'Ребёнок {dou_visit}. Консультация {konsul}')

        if res[0][9]:
            with open('agreement_image.jpg', 'wb') as file:
                file.write(res[0][9])

            pixmap = QPixmap('agreement_image.jpg')
            pixmap = pixmap.scaledToWidth(self.agreement.width())
            self.agreement.setPixmap(pixmap)
        else:
            self.agreement.setText('Нет Согласия')
            self.showAgreementBtn.setEnabled(False)

    def return_back(self):  # Возвращение на прошлое окно
        self.add_form = DBSelectionWidget(self)
        self.add_form.show()
        self.hide()

    def agreement_showing_funk(self):  # Открытие согласия через os
        os.startfile('agreement_image.jpg')

    def edit_funk(self):  # Переход на окно редактирования данных
        self.hide()
        self.add_form = AddKonsFormWidget(self, self.child_id)
        self.add_form.show()

    def keyPressEvent(self, event):  # Выход при нажатии Esc
        if event.key() == Qt.Key_Escape:
            self.hide()
