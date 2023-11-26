import sys
import traceback

from PyQt5.QtWidgets import QApplication

from PasswordEnter import PasswordEnterWidget


def excepthook(exc_type, exc_value, exc_tb):  # Отлов ошибок и вывод их в консоль
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("Oбнаружена ошибка !:", tb)


sys.excepthook = excepthook

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PasswordEnterWidget()
    ex.show()
    sys.exit(app.exec())
