from sys import exit

from PyQt5 import QtWidgets

from qtd_ui import Ui_mw


class GameManager:
    @classmethod
    def start_match(cls):
        UIManager.show_screen(2)
        ...


class UIManager:
    @classmethod
    def show_screen(cls, index: int):
        """ Navigate the UI's stacked widget by index."""
        main_win.ui.sw.setCurrentIndex(index)


class Pazaak(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.init_ui()
        self.setup_buttons()
    
    def init_ui(self):
        self.ui = Ui_mw()
        self.ui.setupUi(self)

    def setup_buttons(self):
        # Main Menu buttons.
        self.ui.mm_btn_start.clicked.connect(lambda: UIManager.show_screen(1))
        self.ui.mm_btn_help.clicked.connect(lambda: print('[DEBUG LOG] HELP button clicked (main menu).'))
        self.ui.mm_btn_exit.clicked.connect(QtWidgets.QApplication.quit)
        # Deck Builder buttons.
        self.ui.db_btn_back.clicked.connect(lambda: UIManager.show_screen(0))
        self.ui.db_btn_play.clicked.connect(GameManager.start_match)
        # Game Screen buttons.
        self.ui.gs_btn_help.clicked.connect(lambda: print('[DEBUG LOG] HELP button clicked (game screen).'))
        self.ui.gs_btn_quit.clicked.connect(lambda: UIManager.show_screen(0))


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    main_win = Pazaak()
    main_win.show()
    # main_win.showFullScreen()
    exit(app.exec_())
