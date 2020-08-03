"""This module automatically solves the Google Chrome version of Minesweeper.

Author: Gene Pan
Date Began: Aug-02-2020
Last Edited: Aug-02-2020
"""

import pyautogui, logging, os, sys

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%H:%M:%S')
#logging.disable(logging.info) # uncomment to block debug log messages

# TODO: Recognize the Minesweeper window

# TODO: Initial startup to get into the game, deciding difficulty, initial click, etc.

# TODO: Create 2D array to represent Minesweeper board

# TODO: Populate array initially as all blank '-'


def im_path(filename):
    """Returns the relative path for the image."""
    return os.path.join('images', filename)

class MinesweeperSolver():
    """Creates a class that automatically solves Google Minesweeper if it can be found on the screen at runtime."""

    DEFAULT_MENU_BAR = im_path('menu_bar_medium.png')

    def __init__(self, difficulty = 'medium'):
        """Initializes accounting for difficulty."""
        logging.debug(f'Creating new MinesweeperSolver on {difficulty} diffuculty')
        self.difficulty = difficulty
        self.menu_bar = im_path('menu_bar_' + self.difficulty.lower() + '.png')
        self.play_button = im_path('play_button.png')
        self.board = []
        self.cell_size = None
        self.menu_region = None
        self.game_region = None

    def prep(self):
        """Prepares the solver by bringing up the Minesweeper game if not already present."""
        logging.debug('Clicking play button! If already clicked, nothing should happen.')
        play_button_pos = pyautogui.locateCenterOnScreen(self.play_button, grayscale = True)
        logging.info(play_button_pos)
        pyautogui.click(play_button_pos)

    def find_default_menu_bar(self):
        self.menu_region = pyautogui.locateOnScreen(MinesweeperSolver.DEFAULT_MENU_BAR)

    def set_difficulty(self):
        """Sets the difficulty according to the call and sets various instance variables dependent on difficulty."""
        if self.difficulty.lower() not in ('easy', 'medium', 'hard'):
            logging.info('Valid difficulty not chosen!')
            sys.exit()

        try:
            pyautogui.moveTo(self.menu_region[0], self.menu_region[1])
        except TypeError:
            logging.info('Game menu not found! Are you sure the game is on screen?')

        pyautogui.moveRel(52, 30)

        if self.difficulty.lower() == 'easy':
            pyautogui.click()
            pyautogui.moveRel(0, 30)
            pyautogui.click()
            self.cell_size = None

        elif self.difficulty.lower() == 'hard':
            pyautogui.click()
            pyautogui.moveRel(0, 70)
            pyautogui.click()
            self.cell_size = None

        else:
            self.cell_size = None

    def find_game_region(self):
        """Test"""
        self.menu_region = pyautogui.locateOnScreen(self.menu_bar)
        self.game_region = None

    def play(self):
        """Solves the game. The main control loop"""
        print('test')

def main():
    m = MinesweeperSolver('hard')
    m.prep()
    m.find_default_menu_bar()
    m.set_difficulty()

main()
