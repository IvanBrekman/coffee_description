import sys
import sqlite3

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QPushButton, QLabel, QHBoxLayout
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QMessageBox

from PyQt5.QtGui import QFont

from PyQt5 import uic

MY_DB = 'coffee.sqlite'


class AddEditCoffeeWindow(QWidget):
    def __init__(self, parent, info=None):
        super().__init__()

        self.info = info
        self.parent = parent
        self.initUI()

    def initUI(self):
        uic.loadUi('addEditCoffeeForm.ui', self)

        if self.info is not None:
            self.sort_name_te.setText(self.info[1])
            self.roasting_te.setText(self.info[2])
            self.ground_cb.setCurrentIndex(int(self.info[3] == 0))
            self.description_pte.document().setPlainText(self.info[4])
            self.price_sb.setValue(self.info[5])
            self.volume_sb.setValue(self.info[6])

            self.save_btn.setText('Изменить')

        self.error_message = QMessageBox()
        self.error_message.setText('Заполните пустые поля')

        self.save_btn.clicked.connect(self.save_changes)

    def save_changes(self):
        info = [self.sort_name_te.text(), self.roasting_te.text(),
                str(int(self.ground_cb.currentText() == 'Молотый')),
                self.description_pte.toPlainText(), self.price_sb.value(), self.volume_sb.value()]
        if any(not bool(el) for el in info):
            self.error_message.show()
            return

        con = sqlite3.connect(MY_DB)
        cur = con.cursor()

        if self.info is not None:
            request = f"""UPDATE coffee SET
            name = '{info[0]}', roasting = '{info[1]}', ground = {info[2]},
            description = '{info[3]}', price = {info[4]}, volume = {info[5]}
            WHERE id = {self.info[0]}"""
        else:
            request = f"""INSERT INTO coffee(name, roasting, ground, description, price, volume)
            VALUES ('{"', '".join(map(str, info))}')"""

        cur.execute(request)

        con.commit()
        con.close()

        self.parent.load_table()


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

        self.error_message = QMessageBox()
        self.error_message.setText('Ячейка не выбрана')

        self.add_btn.clicked.connect(self.add_info)
        self.change_btn.clicked.connect(self.change_info)

    def add_info(self):
        self.add_wnd = AddEditCoffeeWindow(self)
        self.add_wnd.show()

    def change_info(self):
        try:
            note_id = self.coffee_table.item(self.coffee_table.currentItem().row(), 0).text()
            con = sqlite3.connect(MY_DB)
            cur = con.cursor()

            info = cur.execute("""SELECT * FROM coffee WHERE id = ?""", (note_id,)).fetchone()

            self.change_wnd = AddEditCoffeeWindow(self, info)
            self.change_wnd.show()
        except IndexError:
            self.error_message.show()

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
