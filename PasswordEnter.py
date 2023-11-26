from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton

from hashlib import md5
import sqlite3

from MainMenu import MainMenuWidget


class PasswordEnterWidget(QMainWindow):  # Ввод пароля
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
        self.add_form = MainMenuWidget()
        self.add_form.show()
        self.hide()

    def password_check(self):  # Проверка пароля на правильность
        con = sqlite3.connect('database.sql')
        cur = con.cursor()

        res = cur.execute("""SELECT password FROM users""").fetchall()
        if md5(self.password_input.text().encode()).hexdigest() == res[0][0]:
            self.add_form = MainMenuWidget()
            self.add_form.show()
            self.hide()
        else:
            self.label2.setText('Неверно введён пароль')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:  # Активация кнопки "OK" при нажатии Enter
            self.OK_button.click()

        elif event.key() == Qt.Key_Escape:  # Выход при нажатии Esc
            self.hide()
