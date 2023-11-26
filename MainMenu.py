from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import Qt

from AddKonsForm import AddKonsFormWidget
from DBSelection import DBSelectionWidget
from MakeReport import MakeReportWidget
from Settings import SettingsWidget


class MainMenuWidget(QMainWindow):  # Главное меню
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
        self.add_form = AddKonsFormWidget(self)
        self.add_form.show()

    def report_button_funk(self):  # Открытие окна создания отчёта
        self.add_form = MakeReportWidget(self)
        self.add_form.show()

    def check_child_funk(self):  # Открытие окна с БД консультаций
        self.add_form = DBSelectionWidget(self)
        self.add_form.show()

    def settings_button_funk(self):
        self.add_form = SettingsWidget(self)
        self.add_form.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:  # Выход при нажатии Esc
            self.hide()
