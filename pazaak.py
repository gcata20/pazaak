from sys import exit

from PyQt5 import QtWidgets

from qtd_ui import Ui_mw


class Pazaak(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.init_ui()
    
    def init_ui(self):
        self.ui = Ui_mw()
        self.ui.setupUi(self)
        

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    main_win = Pazaak()
    main_win.show()
    # main_win.showFullScreen()
    exit(app.exec_())
