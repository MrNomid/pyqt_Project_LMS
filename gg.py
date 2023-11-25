import os
import sqlite3
from datetime import datetime, timedelta
import sys
import traceback
from hashlib import md5

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QFileDialog, QLabel, QLineEdit, QPushButton
from docxtpl import DocxTemplate


class PasswordEnter(QMainWindow):  # Ввод пароля
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(800, 400, 320, 150)
        self.setWindowTitle('Пароль')
        self.label = QLabel(self)
        self.password_input = QLineEdit(self)
        self.OK_button = QPushButton(self)
        self.label2 = QLabel(self)
        self.OK_button.setText('OK')
        self.label.setFixedWidth(300)
        self.label.move(10, 0)
        self.label2.move(10, 110)
        self.label2.setFixedWidth(300)
        self.label2.setStyleSheet("color: red;")
        self.password_input.move(60, 43)
        self.password_input.resize(200, 20)
        self.OK_button.move(110, 80)

        con = sqlite3.connect('database.sql')
        cur = con.cursor()

        # Проверка на первый заход в программу
        res = cur.execute("""SELECT password FROM users WHERE id = 1""").fetchall()
        if not res[0][0]:
            self.first_enter()
        else:
            self.not_first_enter()

    def first_enter(self):  # При первом заходе в программу
        self.label.setText('Это ваш первый вход в программу. Придумайте пароль:')
        self.OK_button.clicked.connect(self.password_adding)

    def not_first_enter(self):  # При повторном заходе
        self.label.setText('Введите пароль:')
        self.OK_button.clicked.connect(self.password_check)

    def password_adding(self):  # Добавление пароля в БД
        con = sqlite3.connect('database.sql')
        cur = con.cursor()

        res = cur.execute("""UPDATE users SET password = ? WHERE id = 1""", (md5(
            self.password_input.text().encode()).hexdigest(),))
        con.commit()
        self.add_form = MyMainWidget()
        self.add_form.show()
        self.hide()

    def password_check(self):  # Проверка пароля на правильность
        con = sqlite3.connect('database.sql')
        cur = con.cursor()

        res = cur.execute("""SELECT password FROM users""").fetchall()
        if md5(self.password_input.text().encode()).hexdigest() == res[0][0]:
            self.add_form = MyMainWidget()
            self.add_form.show()
            self.hide()
        else:
            self.label2.setText('Неверно введён пароль')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:  # Активация кнопки "OK" при нажатии Enter
            self.OK_button.click()

        elif event.key() == Qt.Key_Escape:  # Выход при нажатии Esc
            self.hide()


class MyMainWidget(QMainWindow):  # Главное меню
    def __init__(self):
        super().__init__()
        uic.loadUi('mainKonsForm.ui', self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Консультация')
        self.addChild.clicked.connect(self.add_button_funk)
        self.finrChild.clicked.connect(self.report_button_funk)
        self.checkChild.clicked.connect(self.check_child_funk)
        self.settings_btn.clicked.connect(self.settings_button_funk)

    def add_button_funk(self):  # Открытие формы добавления
        self.add_form = MyWidget(self)
        self.add_form.show()

    def report_button_funk(self):  # Открытие окна создания отчёта
        self.add_form = ReportWidget(self)
        self.add_form.show()

    def check_child_funk(self):  # Открытие окна с БД консультаций
        self.add_form = MyCheckWidget(self)
        self.add_form.show()

    def settings_button_funk(self):
        self.add_form = SettingsWidget(self)
        self.add_form.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:  # Выход при нажатии Esc
            self.hide()


class MyWidget(QMainWindow):  # Форма добавление и изменения консультации в БД
    def __init__(self, parent=None, child_id=0):
        super().__init__(parent)
        uic.loadUi('KonsForm.ui', self)
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
            self.form = MyInfoWidget(self, self.child_id)
            self.form.show()
            self.hide()

    def back(self):
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:  # Выход при нажатии Esc
            self.back()


class MyCheckWidget(QMainWindow):  # Просмотр БД
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('CheckKonsForm.ui', self)
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
        self.hide()
        self.add_form = MyInfoWidget(self, self.current_id)
        self.add_form.show()

    def back(self):
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:  # Активация кнопки "Найти" при нажатии Enter
            self.printing()

        elif event.key() == Qt.Key_Escape:  # Выход при нажатии Esc
            self.back()


class MyInfoWidget(QMainWindow):  # Вывод подробной информации о конссультации из БД
    def __init__(self, parent=None, child=None):
        super().__init__(parent)
        uic.loadUi('InfoKons.ui', self)
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
        self.add_form = MyCheckWidget(self)
        self.add_form.show()
        self.hide()

    def agreement_showing_funk(self):  # Открытие согласия через os
        os.startfile('agreement_image.jpg')

    def edit_funk(self):  # Переход на окно редактирования данных
        self.hide()
        self.add_form = MyWidget(self, self.child_id)
        self.add_form.show()

    def keyPressEvent(self, event):  # Выход при нажатии Esc
        if event.key() == Qt.Key_Escape:
            self.hide()


class ReportWidget(QMainWindow):  # Создание отчёта по консультациям
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Отчёт')
        uic.loadUi('report_example_form.ui', self)
        self.agreement_blob_data = ''
        self.initUI()

    def initUI(self):
        self.save_us_docx_btn.clicked.connect(self.put_values_into_docx_document)
        self.create_report_btn.clicked.connect(self.put_values_into_column)
        self.back_btn.clicked.connect(self.back)

    def get_values(self):  # Получение данных из БД и их суммирование
        con = sqlite3.connect('database.sql')
        cur = con.cursor()

        from_date = self.from_date.text()
        to_date = self.to_date.text()
        from_date = datetime.strptime(from_date, '%d.%m.%Y').date()
        to_date = datetime.strptime(to_date, '%d.%m.%Y').date()
        ids = cur.execute("""SELECT id from form WHERE
        CAST(STRFTIME('%s', Kons_Date) AS integer) >= CAST(STRFTIME('%s', ?) AS integer)
         AND CAST(STRFTIME('%s', Kons_Date) AS integer) <= CAST(STRFTIME('%s', ?) AS integer)""",
                          (from_date, to_date)).fetchall()
        ids_str = ''
        for id in ids:
            ids_str += str(id[0]) + ', '

        date = datetime.today()
        date1 = (date - timedelta(days=568)).date()
        date2 = (date - timedelta(days=1095)).date()
        date3 = (date - timedelta(days=2555)).date()

        res1 = f"SELECT COUNT(Child_Both_Day) from form WHERE CAST(STRFTIME('%s', Child_Both_Day) AS integer)" \
               f" >= CAST(STRFTIME('%s', '{date1}') AS integer) AND DOU_Visiting = 1 AND id in ({ids_str[:-2]})"
        res2 = f"SELECT COUNT(Child_Both_Day) from form WHERE CAST(STRFTIME('%s', Child_Both_Day)" \
               f"AS integer) >= CAST(STRFTIME('%s', '{date2}') AS integer) AND CAST(STRFTIME('%s', Child_Both_Day) AS" \
               f" integer) < CAST(STRFTIME('%s', '{date1}') AS integer) AND DOU_Visiting = 1 AND id in ({ids_str[:-2]})"
        res3 = f"SELECT COUNT(Child_Both_Day) from form WHERE CAST(STRFTIME('%s', Child_Both_Day)" \
               f"AS integer) >= CAST(STRFTIME('%s', '{date3}') AS integer) AND CAST(STRFTIME('%s', Child_Both_Day) AS" \
               f" integer) < CAST(STRFTIME('%s', '{date2}') AS integer) AND DOU_Visiting = 1 AND id in ({ids_str[:-2]})"
        res4 = f"SELECT COUNT(Child_Both_Day) from form WHERE CAST(STRFTIME('%s', Child_Both_Day) AS integer)" \
               f" >= CAST(STRFTIME('%s', '{date1}') AS integer) AND DOU_Visiting = 0 AND id in ({ids_str[:-2]})"
        res5 = f"SELECT COUNT(Child_Both_Day) from form WHERE CAST(STRFTIME('%s', Child_Both_Day)" \
               f"AS integer) >= CAST(STRFTIME('%s', '{date2}') AS integer) AND CAST(STRFTIME('%s', Child_Both_Day) AS" \
               f" integer) < CAST(STRFTIME('%s', '{date1}') AS integer) AND DOU_Visiting = 0 AND id in ({ids_str[:-2]})"
        res6 = f"SELECT COUNT(Child_Both_Day) from form WHERE CAST(STRFTIME('%s', Child_Both_Day)" \
               f"AS integer) >= CAST(STRFTIME('%s', '{date3}') AS integer) AND CAST(STRFTIME('%s', Child_Both_Day) AS" \
               f" integer) < CAST(STRFTIME('%s', '{date2}') AS integer) AND DOU_Visiting = 0 AND id in ({ids_str[:-2]})"

        self.res1 = cur.execute(res1).fetchall()
        self.res2 = cur.execute(res2).fetchall()
        self.res3 = cur.execute(res3).fetchall()
        self.res4 = cur.execute(res4).fetchall()
        self.res5 = cur.execute(res5).fetchall()
        self.res6 = cur.execute(res6).fetchall()

    def put_values_into_column(self):  # Заполнение таблици данными
        self.get_values()

        self.children1.setText(str(self.res1[0][0]))
        self.children2.setText(str(self.res2[0][0]))
        self.children3.setText(str(self.res3[0][0]))
        self.children4.setText(str(self.res4[0][0]))
        self.children5.setText(str(self.res5[0][0]))
        self.children6.setText(str(self.res6[0][0]))

    def put_values_into_docx_document(self):  # Создание docx документа из данных
        fname = QFileDialog.getExistingDirectory(self, 'Выбрать папку', '.')
        con = sqlite3.connect('database.sql')
        cur = con.cursor()

        organization = cur.execute("""SELECT organization FROM users WHERE id = 1""").fetchall()

        doc = DocxTemplate("Form_exemple.docx")
        context = {'children1': self.res1[0][0], 'children2': self.res2[0][0], 'children3': self.res3[0][0],
                   'children4': self.res4[0][0],
                   'children5': self.res5[0][0], 'children6': self.res6[0][0], 'kindergarten': organization[0][0]}
        doc.render(context)
        doc.save(f"{fname}/отчёт.docx")

    def back(self):  # Выход при нажатии Esc
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.back()


class SettingsWidget(QMainWindow):  # Настройки
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Настройки')
        uic.loadUi('settings_form.ui', self)
        self.initUI()

    def initUI(self):
        con = sqlite3.connect('database.sql')
        cur = con.cursor()

        self.back_btn.clicked.connect(self.back)
        self.save_password_btn.clicked.connect(self.make_new_password)
        self.new_orgenization_btn.clicked.connect(self.save_organization)
        self.organization.setText(cur.execute("""SELECT organization from users WHERE id = 1""").fetchall()[0][0])

    def make_new_password(self):  # Замена пароля
        new_password = self.new_password.text()

        con = sqlite3.connect('database.sql')
        cur = con.cursor()

        res = cur.execute("""UPDATE users SET password = ? WHERE id = 1""", (
            md5(new_password.encode()).hexdigest()),)
        con.commit()

        self.password_status.setText('Пароль успешно сохранён')

    def save_organization(self):  # Замена или добавление организации
        organization = self.organization.text()

        con = sqlite3.connect('database.sql')
        cur = con.cursor()

        res = cur.execute("""UPDATE users SET organization = ? WHERE id = 1""", (organization, ))
        con.commit()
        self.organization_status.setText('Организация успешно изменина')

    def back(self):
        self.hide()

    def keyPressEvent(self, event):  # Выход при нажатии Esc
        if event.key() == Qt.Key_Escape:
            self.back()


def excepthook(exc_type, exc_value, exc_tb):  # Отлов ошибок и вывод их в консоль
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("Oбнаружена ошибка !:", tb)


sys.excepthook = excepthook

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PasswordEnter()
    ex.show()
    sys.exit(app.exec())
