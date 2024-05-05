from random import choice
from sys import exit

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QPixmap

from qtd_ui import Ui_mw


class Card:
    MODS = ['-', '+', '-/+']
    MOD_DICT = {'-': 'minus', '+': 'plus', '-/+': 'dual',
                'minus': '-', 'plus': '+', 'dual': '-/+'}

    def __init__(self, is_dual: bool, value: int, mod: str = None):
        self.is_dual = is_dual
        self.value = value
        self.mod = mod
        if self.is_dual:
            self.active_dual_mod = choice(self.MODS[:2])
        self.set_img_path()
    
    def set_img_path(self, img_path: str):
        self.img_path = img_path


class DeckManager:
    @classmethod
    def init_deck_builder(cls):
        cls.side_deck = [None] * 10
        # - triggers the UI to clear deck slots and disable play button
    
    @classmethod
    def randomize_deck(cls):
        ...


class GameManager:
    @classmethod
    def start_deck_builder(cls):
        DeckManager.init_deck_builder()
        UIManager.show_screen(1)

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
    def __init__(self, *args, **kwargs):
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
        self.ui.db_btn_clear.clicked.connect(DeckManager.init_deck_builder)
        self.ui.db_btn_random.clicked.connect(DeckManager.randomize_deck)
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
