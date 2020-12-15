import sys
import sqlite3

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QPushButton, QLabel, QHBoxLayout
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView

from PyQt5.QtGui import QFont

from PyQt5 import uic

MY_DB = 'coffee.sqlite'


class DescriptionWindow(QWidget):
    def __init__(self, info):
        super().__init__()
        self.description = info
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Описание')
        self.setLayout(QHBoxLayout())

        self.label = QLabel(beauty_description(self.description, 7), self)
        self.label.setFont(QFont("Arial", 16))

        self.layout().addWidget(self.label)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('main.ui', self)

        self.load_table()

        self.coffee_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.coffee_table.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
        self.coffee_table.setColumnHidden(0, True)

    def load_table(self):
        self.more_info_buttons = {}

        con = sqlite3.connect(MY_DB)
        cur = con.cursor()
        
        info = cur.execute("""SELECT * FROM coffee""").fetchall()

        self.coffee_table.setRowCount(0)
        for i in range(len(info)):
            self.coffee_table.setRowCount(self.coffee_table.rowCount() + 1)
            for j in range(len(info[0])):
                if j == 3:
                    item = 'Молотый' if info[i][3] == 1 else 'В зернах'
                elif j == 4:
                    btn = QPushButton('+', self)
                    self.more_info_buttons[btn] = info[i][4]
                    btn.clicked.connect(self.show_description)

                    self.coffee_table.setCellWidget(i, 4, btn)
                    item = ''
                else:
                    item = str(info[i][j])
                self.coffee_table.setItem(i, j, QTableWidgetItem(item))

    def show_description(self):
        self.description_wnd = DescriptionWindow(self.more_info_buttons[self.sender()])
        self.description_wnd.show()


def beauty_description(description: str, size: int) -> str:
    """ Красиво форматирует описание """

    beauty_desc = ''

    for i, word in enumerate(description.split()):
        beauty_desc += word + ' '
        if i % size == size - 1:
            beauty_desc += '\n'

    return beauty_desc.strip()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    wnd = Window()
    wnd.show()

    sys.excepthook = except_hook
    sys.exit(app.exec())
