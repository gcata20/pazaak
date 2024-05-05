from random import choice
from sys import exit

from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw
from PyQt5.QtGui import QIcon, QPixmap

from qtd_ui import Ui_mw


MODS = ['minus', 'plus', 'dual']
VALUES = ['1', '2', '3', '4', '5', '6']


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
    def add_card(cls):
        """Add card to the chosen cards list."""
        new_card = mw.sender().objectName()[3:]
        for i, deck_card in enumerate(cls.chosen_cards):
            if not deck_card:
                cls.chosen_cards[i] = new_card
                obj = mw.db_card_buttons[i]
                mod, value = new_card.split('_')
                img_path = f'assets/card_{mod}_{value}.png'
                UIManager.update_visual(obj, img_path, True)
                break
        if not cls.ready_to_play:
            if all(cls.chosen_cards):
                cls.ready_to_play = True
                UIManager.set_interactive(mw.ui.db_btn_play, True)

    @classmethod
    def reset_deck_builder(cls):
        """Reset the deck builder to initial state."""
        UIManager.set_interactive(mw.ui.db_btn_play, False)
        cls.ready_to_play = False
        cls.chosen_cards = [None] * 10
        for button in mw.db_card_buttons:
            UIManager.update_visual(button, None, False)
    
    @classmethod
    def randomize_deck(cls):
        """Choose 10 random cards for the deck (max 2 copies of each)."""
        cls.reset_deck_builder()
        for i in range(10):
            while True:
                mod = choice(MODS)
                value = choice(VALUES)
                new_card = mod + value
                if cls.chosen_cards.count(new_card) == 2:
                    continue
                break
            cls.chosen_cards[i] = new_card
            obj = mw.db_card_buttons[i]
            img_path = f'assets/card_{mod}_{value}.png'
            UIManager.update_visual(obj, img_path, True)
        cls.ready_to_play = True
        UIManager.set_interactive(mw.ui.db_btn_play, True)

    @classmethod
    def remove_card(cls):
        """Remove existing card from the chosen cards list."""
        if cls.ready_to_play:
            cls.ready_to_play = False
            UIManager.set_interactive(mw.ui.db_btn_play, False)
        card_index = int(mw.sender().objectName()[-1]) - 1
        cls.chosen_cards[card_index] = None
        obj = mw.db_card_buttons[card_index]
        UIManager.update_visual(obj, None, False)


class GameManager:
    @classmethod
    def start_deck_builder(cls):
        DeckManager.reset_deck_builder()
        UIManager.show_screen(1)

    @classmethod
    def start_match(cls):
        UIManager.show_screen(2)
        ...


class UIManager:
    @classmethod
    def set_interactive(cls, button: qtw.QPushButton, new_state: bool):
        """Set a button's state of interactivity and style it accordingly."""
        button.setEnabled(new_state)
        # TODO: change the style sheet based on the new_state (after finishing the art)

    @classmethod
    def show_screen(cls, index: int):
        """ Navigate the UI's stacked widget pages by index.

        Index options:
        - 0: Main Menu
        - 1: Deck Builder
        - 2: Game Screen
        - 3: Help Screen
        """
        mw.ui.sw.setCurrentIndex(index)

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

    @classmethod
    def update_visual(cls, target, img_path: str, enabled_state: bool):
        """Update the image and state of target label or button."""
        if isinstance(target, qtw.QLabel):
            target.setPixmap(QPixmap(img_path))
        elif isinstance(target, qtw.QPushButton):
            target.setIcon(QIcon(img_path))
        target.setEnabled(enabled_state)


class Pazaak(qtw.QMainWindow):
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
        self.ui.mm_btn_exit.clicked.connect(qtw.QApplication.quit)
        # Deck Builder buttons.
        self.ui.db_btn_back.clicked.connect(lambda: UIManager.show_screen(0))
        self.ui.db_btn_play.clicked.connect(GameManager.start_match)
        self.ui.db_btn_clear.clicked.connect(DeckManager.reset_deck_builder)
        self.ui.db_btn_random.clicked.connect(DeckManager.randomize_deck)
        self.av_card_buttons = [self.ui.db_plus_1, self.ui.db_plus_2,
                                self.ui.db_plus_3, self.ui.db_plus_4,
                                self.ui.db_plus_5, self.ui.db_plus_6,
                                self.ui.db_minus_1, self.ui.db_minus_2,
                                self.ui.db_minus_3, self.ui.db_minus_4,
                                self.ui.db_minus_5, self.ui.db_minus_6,
                                self.ui.db_dual_1, self.ui.db_dual_2,
                                self.ui.db_dual_3, self.ui.db_dual_4,
                                self.ui.db_dual_5, self.ui.db_dual_6]
        for button in self.av_card_buttons:
            button.clicked.connect(DeckManager.add_card)
        self.db_card_buttons = [self.ui.db_deck_1, self.ui.db_deck_2,
                                self.ui.db_deck_3, self.ui.db_deck_4,
                                self.ui.db_deck_5, self.ui.db_deck_6,
                                self.ui.db_deck_7, self.ui.db_deck_8,
                                self.ui.db_deck_9, self.ui.db_deck_10]
        for button in self.db_card_buttons:
            button.clicked.connect(DeckManager.remove_card)
        # Game Screen buttons.
        self.ui.gs_btn_help.clicked.connect(lambda: UIManager.toggle_help(2))
        self.ui.gs_btn_quit.clicked.connect(lambda: UIManager.show_screen(0))
        # Help Screen buttons.
        self.ui.hs_btn_close.clicked.connect(lambda: UIManager.toggle_help(3))


if __name__ == '__main__':
    app = qtw.QApplication([])
    mw = Pazaak()
    mw.show()
    # main_win.showFullScreen()
    exit(app.exec_())
