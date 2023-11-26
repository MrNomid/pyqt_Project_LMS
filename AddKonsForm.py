from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5 import uic
from PyQt5.QtCore import Qt

import sqlite3
from datetime import datetime


class AddKonsFormWidget(QMainWindow):  # Форма добавление и изменения консультации в БД
    def __init__(self, parent=None, child_id=0):
        super().__init__(parent)
        uic.loadUi('forms/KonsForm.ui', self)
        self.agreement_blob_data = ''
        self.child_id = child_id
        self.initUI()

    def initUI(self):
        self.all_poles_are_true = False
        self.setWindowTitle('Добавление Ребёнка')
        self.addAgreeing.clicked.connect(self.adding_agreeing)
        self.back_button.clicked.connect(self.back)
        if self.child_id:  # Проверка на изменение консультации
            self.changing_ui()
            self.addButton.clicked.connect(self.changing)
        else:
            self.addButton.clicked.connect(self.adding)

    def get_values(self):  # Получение данных с полей
        con = sqlite3.connect('database.sql')
        cur = con.cursor()
        if self.fioRod.text() and self.fioReb.text() and self.reck.text():

            self.perantfio = self.fioRod.text()  # ФИО родителя
            self.childfio = self.fioReb.text()  # ФИО ребёнка
            self.ch_both_day = self.rebBothDay.text()  # Дата рождения ребёнка
            self.dou_visiting = self.douButons.checkedButton().text()  # Посищает ли ребёнок ДОУ
            self.dou_visiting = 1 if self.dou_visiting == 'Да' else 0  # Превращение duo_visiting в bool
            self.ask = self.reck.text()  # Запрос со слов родителя
            self.theam = self.comboBox.currentText()  # Тема запроса
            self.theam = cur.execute("""SELECT id from KonsTheams WHERE name = ?""", (self.theam,)).fetchall()
            self.konsul = self.KonsButtons.checkedButton().text()  # Первичность консультации
            self.konsul = 1 if self.konsul == 'Первичная' else 0  # Превращение konsul в bool
            self.konsulDate = self.dateKons.text()  # Дата консультации

            self.ch_both_day = datetime.strptime(self.ch_both_day, '%d.%m.%Y').date()
            self.konsulDate = datetime.strptime(self.konsulDate, '%d.%m.%Y').date()
            self.all_poles_are_true = True

        else:
            self.form_error.setText('Форма заполнена не полностью!')

    def adding(self):  # Добавление консультации в БД
        con = sqlite3.connect('database.sql')
        cur = con.cursor()
        self.get_values()
        if self.all_poles_are_true:

            # Добаление Данных Ребёнка в БД
            res = cur.execute("""INSERT INTO form(Perant_Name, Child_Name, Child_Both_Day, DOU_Visiting, Ask,
             Theam, First_Kons, Kons_Date, Agreement) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""", (self.perantfio, self.childfio,
                                                                                             self.ch_both_day,
                                                                                             self.dou_visiting, self.ask,
                                                                                             self.theam[0][0], self.konsul,
                                                                                             self.konsulDate,
                                                                                             self.agreement_blob_data))
            con.commit()
            self.hide()

    def adding_agreeing(self):  # Прикрепление согласия
        fname = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]

        with open(fname, 'rb') as f:
            self.agreement_blob_data = f.read()

    def changing_ui(self):  # Замена UI при изменении данных
        con = sqlite3.connect('database.sql')
        cur = con.cursor()
        res = cur.execute("""SELECT * from form WHERE id = ?""", (self.child_id,)).fetchall()

        self.fioRod.setText(res[0][1])
        self.rebBothDay.setDate(datetime.strptime(res[0][3], '%Y-%m-%d'))
        self.reck.setText(res[0][5])
        self.comboBox.setCurrentIndex(res[0][6] - 1)
        self.dateKons.setDate(datetime.strptime(res[0][8], '%Y-%m-%d'))
        self.fioReb.setText(res[0][2])

        self.radioButton.setChecked(True) if res[0][4] == 1 else self.radioButton_2.setChecked(True)
        self.radioButton_3.setChecked(True) if res[0][7] == 1 else self.radioButton_4.setChecked(True)

        self.addButton.setText('Изменить')
        self.agreement_blob_data = res[0][9]

    def changing(self):  # Замена данных
        from ShowInfo import ShowInfoWidget

        con = sqlite3.connect('database.sql')
        cur = con.cursor()
        self.get_values()
        if self.all_poles_are_true:

            res = cur.execute("""UPDATE form SET Perant_Name = ?, Child_Name = ?, Child_Both_Day = ?, DOU_Visiting = ?,
             Ask = ?, Theam = ?, First_Kons = ?, Kons_Date = ?, Agreement = ? WHERE id = ?""", (self.perantfio,
                                                                                                self.childfio,
                                                                                                self.ch_both_day,
                                                                                                self.dou_visiting, self.ask,
                                                                                                self.theam[0][0],
                                                                                                self.konsul,
                                                                                                self.konsulDate,
                                                                                                self.agreement_blob_data,
                                                                                                self.child_id))
            con.commit()
            self.form = ShowInfoWidget(self, self.child_id)
            self.form.show()
            self.hide()

    def back(self):
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:  # Выход при нажатии Esc
            self.back()