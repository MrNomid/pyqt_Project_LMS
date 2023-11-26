from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5 import uic
from PyQt5.QtCore import Qt

import sqlite3
from datetime import datetime, timedelta
from docxtpl import DocxTemplate


class MakeReportWidget(QMainWindow):  # Создание отчёта по консультациям
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
