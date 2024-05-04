from sys import exit

from PyQt5 import QtWidgets

from qtd_ui import Ui_mw


class GameManager:
    @classmethod
    def start_deck_builder(cls):
        UIManager.show_screen(1)
        ...

    @classmethod
    def start_match(cls):
        UIManager.show_screen(2)
        ...


class UIManager:
    @classmethod
    def show_screen(cls, index: int):
        """ Navigate the UI's stacked widget pages by index.

        Index options:
        - 0: Main Menu
        - 1: Deck Builder
        - 2: Game Screen
        - 3: Help Screen
        """
        main_win.ui.sw.setCurrentIndex(index)

    @classmethod
    def toggle_help(cls, source_page_index: int):
        """Navigate to and from the help screen from anywhere.

        Achieved by storing the page from where the help screen was accessed.
        """
        if not source_page_index == 3:
            cls.index_to_help = source_page_index
            cls.show_screen(3)
        else:
            cls.show_screen(cls.index_to_help)


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
        self.ui.mm_btn_start.clicked.connect(GameManager.start_deck_builder)
        self.ui.mm_btn_help.clicked.connect(lambda: UIManager.toggle_help(0))
        self.ui.mm_btn_exit.clicked.connect(QtWidgets.QApplication.quit)
        # Deck Builder buttons.
        self.ui.db_btn_back.clicked.connect(lambda: UIManager.show_screen(0))
        self.ui.db_btn_play.clicked.connect(GameManager.start_match)
        # Game Screen buttons.
        self.ui.gs_btn_help.clicked.connect(lambda: UIManager.toggle_help(2))
        self.ui.gs_btn_quit.clicked.connect(lambda: UIManager.show_screen(0))
        # Help Screen buttons.
        self.ui.hs_btn_close.clicked.connect(lambda: UIManager.toggle_help(3))


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    main_win = Pazaak()
    main_win.show()
    # main_win.showFullScreen()
    exit(app.exec_())
