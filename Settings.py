from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import Qt

import sqlite3
from hashlib import md5


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
            md5(new_password.encode()).hexdigest(),))
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
