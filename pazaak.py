from random import choice, shuffle
from sys import exit

from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw
from PyQt5.QtGui import QIcon, QPixmap

from qtd_ui import Ui_mw


MODS = ['minus', 'plus', 'dual']
VALUES = range(1, 7)
# MOD_DICT = {'-': 'minus', '+': 'plus', '-/+': 'dual',
#                 'minus': '-', 'plus': '+', 'dual': '-/+'}


class Card:
    def __init__(self, value: int, mod: str = None):
        self.value = value
        self.mod = mod
        if mod == 'dual':
            self.is_dual = True
            self.active_dual_mod = choice(['minus', 'plus'])
        else:
            self.is_dual = False
        self.set_img_path()
    
    def set_img_path(self):
        new_mod = self.mod
        if self.is_dual:
            if self.active_dual_mod == 'minus':
                new_mod = 'dual_minus'
            elif self.active_dual_mod == 'plus':
                new_mod = 'dual_plus'
        self.img_path = f'assets/card_{new_mod}_{self.value}.png'


class DeckManager:
    @classmethod
    def add_card(cls):
        """Add card to the chosen cards list."""
        new_card = mw.sender().objectName()[3:]
        for i, deck_card in enumerate(cls.chosen_cards):
            if not deck_card:
                cls.chosen_cards[i] = new_card
                button = mw.db_deck_cards[i]
                mod, value = new_card.split('_')
                img_path = f'assets/card_{mod}_{value}.png'
                UIManager.update_visual(button, True, img_path)
                break
        if not cls.ready_to_play:
            if all(cls.chosen_cards):
                cls.ready_to_play = True
                UIManager.update_visual(mw.ui.db_btn_play, True)

    @classmethod
    def init_deck_builder(cls):
        """Reset the deck builder to initial state."""
        UIManager.update_visual(mw.ui.db_btn_play, False)
        cls.ready_to_play = False
        cls.chosen_cards = [None] * 10
        for button in mw.db_deck_cards:
            UIManager.update_visual(button, False, '')
    
    @classmethod
    def randomize_deck(cls):
        """Choose 10 random cards for the deck (max 2 copies of each)."""
        cls.init_deck_builder()
        for i in range(10):
            while True:
                mod = choice(MODS)
                value = choice(VALUES)
                new_card = f'{mod}_{value}'
                if cls.chosen_cards.count(new_card) == 2:
                    continue
                break
            cls.chosen_cards[i] = new_card
            button = mw.db_deck_cards[i]
            img_path = f'assets/card_{mod}_{value}.png'
            UIManager.update_visual(button, True, img_path)
        cls.ready_to_play = True
        UIManager.update_visual(mw.ui.db_btn_play, True)

    @classmethod
    def remove_card(cls):
        """Remove existing card from the chosen cards list."""
        if cls.ready_to_play:
            cls.ready_to_play = False
            UIManager.update_visual(mw.ui.db_btn_play, False)
        card_index = int(mw.sender().objectName()[-1]) - 1
        cls.chosen_cards[card_index] = None
        button = mw.db_deck_cards[card_index]
        UIManager.update_visual(button, False, '')


class GameManager:
    @classmethod
    def to_deck_builder(cls):
        UIManager.show_screen(1)
        DeckManager.init_deck_builder()

    @classmethod
    def to_game_screen(cls):
        UIManager.show_screen(2)
        MatchManager.start_match()
    
    @classmethod
    def toggle_help(cls, source_page_index: int):
        """Navigate to and from the help screen from anywhere.

        Achieved by storing the page from where the help screen was accessed.
        """
        if not source_page_index == 3:
            cls.index_to_help = source_page_index
            UIManager.show_screen(3)
        else:
            UIManager.show_screen(cls.index_to_help)


class MatchManager:
    @classmethod
    def init_table(cls):
        """Initialize game elements for the start of a new set."""
        # Set indicators.
        set_indicators = mw.player_sets + mw.opp_sets
        inactive_set_img = 'assets/set_inactive.png'
        for label in set_indicators:
            UIManager.update_visual(label, new_img_path=inactive_set_img)
        # Turn indicators.
        for label in [mw.player_turn, mw.ui.gs_opp_turn]:
            UIManager.update_visual(label, new_img_path='')
        # Scores and score indicators.
        Player.current_total = 0
        Opponent.current_total = 0
        for label in [mw.ui.gs_player_total, mw.ui.gs_opp_total]:
            UIManager.update_total(label, 0)
        # Table card slots.
        card_slots = mw.player_table_cards + mw.opp_table_cards
        for label in card_slots:
            UIManager.update_visual(label, False, '')
    
    @classmethod
    def start_match(cls):
        """Execute logic for starting a new match."""
        # Generate player and opponent hands.
        Player.generate_hand()
        Opponent.generate_hand()
         # Disable interactible buttons.
        UIManager.toggle_gs_buttons(False)
        # Show player's hand cards (and flip icons where applicable).
        for i, button in enumerate(mw.player_hand_cards):
            img_path = Player.hand_cards[i].img_path
            UIManager.update_visual(button, new_img_path=img_path)
            flip_button = mw.player_flip_buttons[i]
            if Player.hand_cards[i].is_dual:
                img_path = 'assets/flip_card.png'
                UIManager.update_visual(flip_button, new_img_path=img_path)
            else:
                UIManager.update_visual(flip_button, new_img_path='')
        # Show opponent's hand cards.
        card_back_img = 'assets/card_back.png'
        for label in mw.opp_hand_cards:
            UIManager.update_visual(label, new_img_path=card_back_img)
        # Start new set.
        cls.start_set()
    
    @classmethod
    def start_set(cls):
        """Execut logic for starting a new set."""
        cls.init_table()
        ...


class Opponent:
    current_total = 0

    @classmethod
    def generate_hand(cls):
        """Generate a random 4-card hand from a random deck."""
        side_deck = [None] * 10
        cls.hand_cards = [None] * 4
        for i in range(10):
            while True:
                mod = choice(MODS)
                value = choice(VALUES)
                new_card = f'{mod}_{value}'
                if side_deck.count(new_card) == 2:
                    continue
                break
            side_deck[i] = new_card
        for _ in range(8):
            shuffle(side_deck)
        for i in range(4):
            random_card = side_deck.pop()
            value = int(random_card[-1])
            mod = random_card[:-2]
            new_card = Card(value, mod)
            cls.hand_cards[i] = new_card
    ...


class Player:
    current_total = 0
    hand_cards = [None] * 4
    
    @classmethod
    def generate_hand(cls):
        """Generate a random 4-card hand from the chosen side deck."""
        cls.hand_cards = [None] * 4
        for _ in range(8):
            shuffle(DeckManager.chosen_cards)
        for i in range(4):
            chosen_card = DeckManager.chosen_cards.pop()
            value = int(chosen_card[-1])
            mod = chosen_card[:-2]
            new_card = Card(value, mod)
            cls.hand_cards[i] = new_card
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
        mw.ui.sw.setCurrentIndex(index)

    @classmethod
    def toggle_gs_buttons(cls, interactible_state: bool):
        """Toggle interactivity of all buttons on the game screen."""
        buttons = [mw.ui.gs_btn_help, mw.ui.gs_btn_endturn,
                   mw.ui.gs_btn_stand, mw.ui.gs_btn_quit]
        for button in buttons:
            UIManager.update_visual(button, interactible_state)
        for i, card in enumerate(Player.hand_cards):
            if card is not None:
                card_button = mw.player_hand_cards[i]
                flip_button = mw.player_flip_buttons[i]
                UIManager.update_visual(card_button, interactible_state)
                UIManager.update_visual(flip_button, interactible_state)

    @classmethod
    def update_total(cls, label: qtw.QLabel, value: int):
        """Change the text and color of the total label."""
        label.setText(str(value))
        color_dict = {value < 20: 'white',
                      value == 20: 'lime',
                      value > 20: 'red'}
        label.setStyleSheet(f'color: {color_dict[True]}')

    @classmethod
    def update_visual(cls,
                      target,
                      new_enabled_state: bool = None,
                      new_img_path: str = None):
        """Change the state and image of the target button or label.

        Use an empty string as new_img_path to remove the image altogether.
        """
        if new_enabled_state is not None:
            target.setEnabled(new_enabled_state)
        if new_img_path is not None:
            if new_img_path == '':
                new_img_path = None
            if isinstance(target, qtw.QPushButton):
                target.setIcon(QIcon(new_img_path))
            elif isinstance(target, qtw.QLabel):
                target.setPixmap(QPixmap(new_img_path))
    

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
        self.ui.mm_btn_start.clicked.connect(GameManager.to_deck_builder)
        self.ui.mm_btn_help.clicked.connect(lambda: GameManager.toggle_help(0))
        self.ui.mm_btn_exit.clicked.connect(qtw.QApplication.quit)
        # Deck Builder buttons.
        self.ui.db_btn_back.clicked.connect(lambda: UIManager.show_screen(0))
        self.ui.db_btn_play.clicked.connect(GameManager.to_game_screen)
        self.ui.db_btn_clear.clicked.connect(DeckManager.init_deck_builder)
        self.ui.db_btn_random.clicked.connect(DeckManager.randomize_deck)
        db_av_cards = [self.ui.db_plus_1, self.ui.db_plus_2,
                       self.ui.db_plus_3, self.ui.db_plus_4,
                       self.ui.db_plus_5, self.ui.db_plus_6,
                       self.ui.db_minus_1, self.ui.db_minus_2,
                       self.ui.db_minus_3, self.ui.db_minus_4,
                       self.ui.db_minus_5, self.ui.db_minus_6,
                       self.ui.db_dual_1, self.ui.db_dual_2,
                       self.ui.db_dual_3, self.ui.db_dual_4,
                       self.ui.db_dual_5, self.ui.db_dual_6]
        for button in db_av_cards:
            button.clicked.connect(DeckManager.add_card)
        self.db_deck_cards = [self.ui.db_deck_1, self.ui.db_deck_2,
                              self.ui.db_deck_3, self.ui.db_deck_4,
                              self.ui.db_deck_5, self.ui.db_deck_6,
                              self.ui.db_deck_7, self.ui.db_deck_8,
                              self.ui.db_deck_9, self.ui.db_deck_10]
        for button in self.db_deck_cards:
            button.clicked.connect(DeckManager.remove_card)
        # Game Screen buttons and labels.
        self.ui.gs_btn_help.clicked.connect(lambda: GameManager.toggle_help(2))
        self.ui.gs_btn_quit.clicked.connect(lambda: UIManager.show_screen(0))
        self.player_sets = [self.ui.gs_player_set_1,
                            self.ui.gs_player_set_2,
                            self.ui.gs_player_set_3]
        self.opp_sets = [self.ui.gs_opp_set_1,
                         self.ui.gs_opp_set_2,
                         self.ui.gs_opp_set_3]
        self.player_turn = self.ui.gs_player_turn
        self.opp_turn = self.ui.gs_opp_turn
        self.player_table_cards = [self.ui.gs_player_slot_1,
                                   self.ui.gs_player_slot_2,
                                   self.ui.gs_player_slot_3,
                                   self.ui.gs_player_slot_4,
                                   self.ui.gs_player_slot_5,
                                   self.ui.gs_player_slot_6,
                                   self.ui.gs_player_slot_7,
                                   self.ui.gs_player_slot_8,
                                   self.ui.gs_player_slot_9]
        self.opp_table_cards = [self.ui.gs_opp_slot_1,
                                self.ui.gs_opp_slot_2,
                                self.ui.gs_opp_slot_3,
                                self.ui.gs_opp_slot_4,
                                self.ui.gs_opp_slot_5,
                                self.ui.gs_opp_slot_6,
                                self.ui.gs_opp_slot_7,
                                self.ui.gs_opp_slot_8,
                                self.ui.gs_opp_slot_9]
        self.player_hand_cards = [self.ui.gs_player_hand_1,
                                  self.ui.gs_player_hand_2,
                                  self.ui.gs_player_hand_3,
                                  self.ui.gs_player_hand_4]
        self.player_flip_buttons = [self.ui.gs_flip_1, self.ui.gs_flip_2,
                                    self.ui.gs_flip_3, self.ui.gs_flip_4]
        self.opp_hand_cards = [self.ui.gs_opp_hand_1, self.ui.gs_opp_hand_2,
                               self.ui.gs_opp_hand_3, self.ui.gs_opp_hand_4]
        # Help Screen buttons.
        self.ui.hs_btn_close.clicked.connect(lambda: GameManager.toggle_help(3))


if __name__ == '__main__':
    app = qtw.QApplication([])
    mw = Pazaak()
    mw.show()
    # main_win.showFullScreen()
    exit(app.exec_())
