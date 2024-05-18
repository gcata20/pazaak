from random import choice, shuffle
from sys import exit

from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw
from PyQt5.QtGui import QIcon, QPixmap

from qtd_ui import Ui_mw


MODS = ['minus', 'plus', 'dual']
VALUES = range(1, 7)


class Card:
    def __init__(self, value: int, mod: str = None):
        self.value = value
        self.mod = mod
        if mod == 'dual':
            self.is_dual = True
            self.active_mod = choice(['minus', 'plus'])
        else:
            self.active_mod = mod
            self.is_dual = False
        self.set_img_path()
    
    def __str__(self) -> str:
        if not self.is_dual:
            return f'{self.mod} {self.value}'
        else:
            return f'{self.mod} {self.value} ({self.active_mod})'
    
    def flip_mod(self):
        if self.mod == 'dual':
            if self.active_mod == 'minus':
                self.active_mod = 'plus'
            else:
                self.active_mod = 'minus'
            self.set_img_path()
    
    def set_img_path(self):
        new_mod = self.mod
        if self.is_dual:
            if self.active_mod == 'minus':
                new_mod = 'dual_minus'
            elif self.active_mod == 'plus':
                new_mod = 'dual_plus'
        self.img_path = f'assets/card_{new_mod}_{self.value}.png'


class Competitor:
    total = 0
    side_deck = []
    hand_cards = []
    is_standing = False
    has_full_table = False
    sets_won = 0

    @classmethod
    def generate_hand(cls):
        """Generate a random 4-card hand from the side deck."""
        cls.hand_cards = [None] * 4
        for _ in range(8):
            shuffle(cls.side_deck)
        for i in range(4):
            chosen_card = cls.side_deck.pop()
            value = int(chosen_card[-1])
            mod = chosen_card[:-2]
            cls.hand_cards[i] = Card(value, mod)
    
    @classmethod
    def generate_side_deck(cls):
        """Generate a random 10-card side deck."""
        cls.side_deck.clear()
        for i in range(10):
            while True:
                mod = choice(MODS)
                value = choice(VALUES)
                new_card = f'{mod}_{value}'
                if cls.side_deck.count(new_card) == 2:
                    continue
                break
            cls.side_deck.append(new_card)


class GameManager:
    @classmethod
    def add_card(cls):
        """Add chosen card to the player's side deck."""
        chosen_card = mw.sender().objectName()[3:]
        for i, deck_card in enumerate(Player.side_deck):
            if not deck_card:
                Player.side_deck[i] = chosen_card
                button = mw.db_deck_cards[i]
                mod, value = chosen_card.split('_')
                img_path = f'assets/card_{mod}_{value}.png'
                UIManager.update_visual(button, True, img_path)
                break
        if not cls.ready_to_play:
            if all(Player.side_deck):
                cls.ready_to_play = True
                UIManager.update_visual(mw.ui.db_btn_play, True)

    @classmethod
    def init_deck_builder(cls):
        """Set the deck builder to its initial state."""
        UIManager.update_visual(mw.ui.db_btn_play, False)
        cls.ready_to_play = False
        Player.side_deck = [None] * 10
        for button in mw.db_deck_cards:
            UIManager.update_visual(button, False, '')
    
    @classmethod
    def randomize_deck(cls):
        """Generate a random side deck and show it on the deck builder."""
        cls.init_deck_builder()
        Player.generate_side_deck()
        for i, card in enumerate(Player.side_deck):
            button = mw.db_deck_cards[i]
            mod = card[:-2]
            value = int(card[-1])
            img_path = f'assets/card_{mod}_{value}.png'
            UIManager.update_visual(button, True, img_path)
        cls.ready_to_play = True
        UIManager.update_visual(mw.ui.db_btn_play, True)

    @classmethod
    def remove_card(cls):
        """Remove chosen card from the player's side deck."""
        if cls.ready_to_play:
            cls.ready_to_play = False
            UIManager.update_visual(mw.ui.db_btn_play, False)
        chosen_card_index = int(mw.sender().objectName()[-1]) - 1
        Player.side_deck[chosen_card_index] = None
        button = mw.db_deck_cards[chosen_card_index]
        UIManager.update_visual(button, False, '')

    @classmethod
    def resolve_end(cls):
        sender_name = mw.sender().objectName()
        if 'set' in sender_name:
            mw.ui.popup_set.hide()
            Match.start_set()
        elif 'match' in sender_name:
            mw.ui.popup_match.hide()
            UIManager.show_screen(0)

    @classmethod
    def to_deck_builder(cls):
        UIManager.show_screen(1)
        cls.init_deck_builder()

    @classmethod
    def to_game_screen(cls):
        UIManager.show_screen(2)
        Match.start_match()
    
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


class Match:
    house_deck = []
    set_is_over = False
    match_is_over = False

    @classmethod
    def evaluate_turn(cls, caller: str):
        if Player.total > 20:
            cls.set_is_over = True
            Opponent.sets_won += 1
            mw.ui.text_info_set.setText('You lost the set.')
        elif Opponent.total > 20:
            cls.set_is_over = True
            Player.sets_won += 1
            mw.ui.text_info_set.setText('You won the set.')
        elif Player.is_standing and Opponent.is_standing:
            cls.set_is_over = True
            if Player.total == Opponent.total:
                mw.ui.text_info_set.setText('The set is a draw.')
            elif Player.total > Opponent.total:
                Player.sets_won += 1
                mw.ui.text_info_set.setText('You won the set.')
            elif Player.total < Opponent.total:
                Opponent.sets_won += 1
                mw.ui.text_info_set.setText('You lost the set.')
            
        if Player.sets_won == 3:
            cls.match_is_over = True
            mw.ui.text_info_match.setText('You won the match.')
        elif Opponent.sets_won == 3:
            cls.match_is_over = True
            mw.ui.text_info_match.setText('You lost the match.')
        
        if not cls.set_is_over:
            if caller == 'player':
                if not Opponent.is_standing:
                    qtc.QTimer.singleShot(200, Opponent.play_turn)
                else:
                    qtc.QTimer.singleShot(800, Player.play_turn)
            elif caller == 'opponent':
                if not Player.is_standing:
                    qtc.QTimer.singleShot(1000, Player.play_turn)
                else:
                    qtc.QTimer.singleShot(900, Opponent.play_turn)
        elif cls.set_is_over and not cls.match_is_over:
            qtc.QTimer.singleShot(800, mw.ui.popup_set.show)
        elif cls.match_is_over:
            qtc.QTimer.singleShot(800, mw.ui.popup_match.show)

    @classmethod
    def draw_card(cls, target: str) -> int:
        """Draw card from the house deck. Show it on screen. Return it.

        Options for the 'target' parameter:
        - player
        - opponent

        - mw.player_table_cards: for the player's list
        - mw.opp_table_cards: for the opponent's list
        """
        if target == 'player':
            target_slots = mw.player_table_cards
        elif target == 'opponent':
            target_slots = mw.opp_table_cards
        else:
            raise SyntaxError('Invalid use of the draw_card function.')
        drawn_card_value = cls.house_deck.pop()
        for label in target_slots:
            if not label.isEnabled():
                img_path = f'assets/card_basic_{drawn_card_value}.png'
                UIManager.update_visual(label, True, img_path)
                if label.objectName()[-1] == '9':
                    if target == 'player':
                        Player.has_full_table = True
                    elif target == 'opponent':
                        Opponent.has_full_table = True
                break
        return drawn_card_value

    @classmethod
    def end_turn(cls):
        UIManager.toggle_gs_buttons(False)
        cls.evaluate_turn('player')

    @classmethod
    def flip_card(cls):
        sender_index = int(mw.sender().objectName()[-1]) - 1
        card = Player.hand_cards[sender_index]
        card.flip_mod()
        label = mw.player_hand_cards[sender_index]
        img_path = card.img_path
        UIManager.update_visual(label, new_img_path=img_path)

    @classmethod
    def generate_house_deck(cls, shuffles: int = 8) -> None:
        """Generate a list of cards representing the house's deck.

        The optional parameter 'shuffles' shuffles it that many times.
        """
        cls.house_deck.clear()
        for n in range(10):
            for _ in range(4):
                cls.house_deck.append(n + 1)
        for _ in range(shuffles):
            shuffle(cls.house_deck)

    @classmethod
    def init_table(cls):
        """Initialize game elements for the start of a new set."""
        # Turn indicators.
        for label in [mw.player_turn, mw.ui.gs_opp_turn]:
            UIManager.update_visual(label, new_img_path='')
        # Scores and score indicators.
        Player.total = 0
        Opponent.total = 0
        for label in [mw.ui.gs_player_total, mw.ui.gs_opp_total]:
            UIManager.update_total(label, 0)
        # Table card slots.
        card_slots = mw.player_table_cards + mw.opp_table_cards
        for label in card_slots:
            UIManager.update_visual(label, False, '')
    
    @classmethod
    def play_hand_card(cls):
        if Player.has_played_card:
            return
        sender_index = int(mw.sender().objectName()[-1]) - 1
        card = Player.hand_cards[sender_index]
        for label in mw.player_table_cards:
            if not label.isEnabled():
                Player.has_played_card = True
                UIManager.update_visual(label, True, card.img_path)
                hand_card_button = mw.player_hand_cards[sender_index]
                UIManager.update_visual(hand_card_button, False, '')
                if card.mod == 'dual':
                    flip_button = mw.player_flip_buttons[sender_index]
                    UIManager.update_visual(flip_button, False, '')
                if card.active_mod == 'plus':
                    Player.total += card.value
                elif card.active_mod == 'minus':
                    Player.total -= card.value
                    if Player.total < 0:
                        Player.total = 0
                UIManager.update_total(mw.ui.gs_player_total, Player.total)
                Player.hand_cards[sender_index] = None
                break

    @classmethod
    def stand(cls):
        Player.is_standing = True
        cls.end_turn()

    @classmethod
    def start_match(cls):
        """Execute logic for starting a new match."""
        cls.match_is_over = False
        # Generate player and opponent hands.
        Player.generate_hand()
        Opponent.generate_side_deck()
        Opponent.generate_hand()
         # Disable interactible buttons.
        UIManager.toggle_gs_buttons(False)
        # Initialize set logic and indicators.
        Player.sets_won = 0
        Opponent.sets_won = 0
        set_indicators = mw.player_sets + mw.opp_sets
        inactive_img = 'assets/set_inactive.png'
        for label in set_indicators:
            UIManager.update_visual(label, new_img_path=inactive_img)
        # Show player's hand cards (and flip icons where applicable).
        for i, button in enumerate(mw.player_hand_cards):
            img_path = Player.hand_cards[i].img_path
            UIManager.update_visual(button, new_img_path=img_path)
            flip_button = mw.player_flip_buttons[i]
            if Player.hand_cards[i].is_dual:
                img_path = 'assets/flip_card.png'
                UIManager.update_visual(flip_button, new_img_path=img_path)
            else:
                UIManager.update_visual(flip_button, False, '')
        # Show opponent's hand cards.
        card_back_img = 'assets/card_back.png'
        for label in mw.opp_hand_cards:
            UIManager.update_visual(label, new_img_path=card_back_img)
        # Start new set.
        cls.start_set()
    
    @classmethod
    def start_set(cls):
        """Execute logic for starting a new set."""
        cls.set_is_over = False
        cls.generate_house_deck()
        cls.init_table()
        Player.is_standing = False
        Player.has_full_table = False
        Opponent.is_standing = False
        Opponent.has_full_table = False
        qtc.QTimer.singleShot(500, Player.play_turn)


class Opponent(Competitor):
    @classmethod
    def make_decision(cls):
        if Player.is_standing and cls.total > Player.total:
            cls.is_standing = True
            print('[DEBUG LOG] Opponent is standing.')
        elif cls.total >= 18:
            cls.is_standing = True
            print('[DEBUG LOG] Opponent is standing.')

    @classmethod
    def play_turn(cls):
        if not cls.is_standing:
            drawn_card_value = Match.draw_card('opponent')
            cls.total += drawn_card_value
            UIManager.update_total(mw.ui.gs_opp_total, cls.total)
            cls.make_decision()
            Match.evaluate_turn('opponent')


class Player(Competitor):
    has_played_card = False
    
    @classmethod
    def play_turn(cls):
        if not Player.is_standing:
            cls.has_played_card = False
            drawn_card_value = Match.draw_card('player')
            Player.total += drawn_card_value
            UIManager.update_total(mw.ui.gs_player_total, Player.total)
            if Player.total == 20 or Player.has_full_table:
                Match.stand()
            else:
                UIManager.toggle_gs_buttons(True)


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
                UIManager.update_visual(card_button, interactible_state)
                if card.is_dual:
                    flip_button = mw.player_flip_buttons[i]
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
        self.setup_visuals()
    
    def init_ui(self):
        self.ui = Ui_mw()
        self.ui.setupUi(self)

    def setup_visuals(self):
        # Main Menu buttons.
        self.ui.mm_btn_start.clicked.connect(GameManager.to_deck_builder)
        self.ui.mm_btn_help.clicked.connect(lambda: GameManager.toggle_help(0))
        self.ui.mm_btn_exit.clicked.connect(qtw.QApplication.quit)
        # Deck Builder buttons.
        self.ui.db_btn_back.clicked.connect(lambda: UIManager.show_screen(0))
        self.ui.db_btn_play.clicked.connect(GameManager.to_game_screen)
        self.ui.db_btn_clear.clicked.connect(GameManager.init_deck_builder)
        self.ui.db_btn_random.clicked.connect(GameManager.randomize_deck)
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
            button.clicked.connect(GameManager.add_card)
        self.db_deck_cards = [self.ui.db_deck_1, self.ui.db_deck_2,
                              self.ui.db_deck_3, self.ui.db_deck_4,
                              self.ui.db_deck_5, self.ui.db_deck_6,
                              self.ui.db_deck_7, self.ui.db_deck_8,
                              self.ui.db_deck_9, self.ui.db_deck_10]
        for button in self.db_deck_cards:
            button.clicked.connect(GameManager.remove_card)
        # Game Screen buttons and labels.
        self.ui.gs_btn_help.clicked.connect(lambda: GameManager.toggle_help(2))
        self.ui.gs_btn_quit.clicked.connect(lambda: UIManager.show_screen(0))
        self.ui.gs_btn_endturn.clicked.connect(Match.end_turn)
        self.ui.gs_btn_stand.clicked.connect(Match.stand)
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
        for button in self.player_hand_cards:
            button.clicked.connect(Match.play_hand_card)
        self.player_flip_buttons = [self.ui.gs_flip_1, self.ui.gs_flip_2,
                                    self.ui.gs_flip_3, self.ui.gs_flip_4]
        for button in self.player_flip_buttons:
            button.clicked.connect(Match.flip_card)
        self.opp_hand_cards = [self.ui.gs_opp_hand_1, self.ui.gs_opp_hand_2,
                               self.ui.gs_opp_hand_3, self.ui.gs_opp_hand_4]
        # Help Screen buttons.
        self.ui.hs_btn_close.clicked.connect(lambda: GameManager.toggle_help(3))
        # Set and Match Popups.
        self.ui.btn_ok_set.clicked.connect(GameManager.resolve_end)
        self.ui.btn_ok_match.clicked.connect(GameManager.resolve_end)
        self.ui.popup_set.hide()
        self.ui.popup_match.hide()


if __name__ == '__main__':
    app = qtw.QApplication([])
    mw = Pazaak()
    mw.show()
    # main_win.showFullScreen()
    exit(app.exec_())
