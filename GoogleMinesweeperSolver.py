"""This module automatically solves the Google Chrome version of Minesweeper.

Author: Gene Pan
Date Began: Aug-02-2020
Last Edited: Jan-10-2021
"""

import pyautogui, logging, os, sys, cv2
from PIL import Image
pyautogui.PAUSE = 0

# logging.basicConfig(
#     format='%(asctime)s,%(msecs)d %(levelname)-8s [%(name)s:%(filename)s:%(lineno)d] %(message)s',
#     datefmt='%Y-%m-%d:%H:%M:%S',
#     level=logging.DEBUG)

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(asctime)s.%(msecs)03d: [%(lineno)d] %(message)s', datefmt='%H:%M:%S')
# logging.disable(logging.info) # uncomment to block debug log messages

# TODO: Find algorithm for probability

# TODO: Create cell class

# TODO: Update board function

def im_path(filename):
    """Returns the relative path for the image."""
    return os.path.join('images', filename)


class MinesweeperCell():
    """MinesweeperCell represents an individual cell in the MinesweeperSolver class."""

    HIDDEN_COLOR_1 = (170, 215, 81)  # Alternatively: (162, 209, 73) although the tolerances should recognize this anyways
    HIDDEN_COLOR_2 = (162, 209, 73)
    BLANK_COLOR_1 = (215, 184, 153)  
    BLANK_COLOR_2 = (229, 194, 159)
    ONE_COLOR = (25, 118, 210)
    TWO_COLOR = (69, 146, 67)
    THREE_COLOR = (211, 47, 47)
    FOUR_COLOR = (155, 85, 159)
    FIVE_COLOR = (254, 144, 3)

    COLOR_TOLERANCE = 20  # Distance in RGB value
    POSITION_TOLERANCE = 5  # how many pixels around center will the color be searched for

    HIDDEN_IMAGE = im_path('hidden_light.png')
    BLANK_IMAGE = im_path('blank_light.png')
    ONE_IMAGE = im_path('cell_1.png')
    TWO_IMAGE = im_path('cell_2.png')
    THREE_IMAGE = im_path('cell_3.png')
    FOUR_IMAGE = im_path('cell_4.png')
    FIVE_IMAGE = im_path('cell_5.png')

    def __init__(self, ms_solver, coordinate):
        logging.debug(f'Creating cell at ({coordinate[0], coordinate[1]})')
        self.parent = ms_solver
        self.cell_region = (None, None, None, None)
        self.state = 'U'
        self.color_position = None
        self.coordinate = coordinate  # (x, y) tuple
        self.neighbors = []

    def __repr__(self):
        return self.state

    def identify_neighbors(self):
        for x in range(self.coordinate[0] - 1, self.coordinate[0] + 2):
            for y in range(self.coordinate[1] - 1, self.coordinate[1] + 2):
                if (x, y) != self.coordinate:
                    try:
                        neighbor = self.parent.board[y][x]
                        self.neighbors.append(neighbor)
                        logging.debug(f'Neighbor for cell at ({self.coordinate[0], self.coordinate[1]}): ({x}, {y})')
                    except IndexError:
                        logging.debug('Neighbor does not exist. Likely edge/corner cell.')

    def color_match(self, color):
        logging.info(f'Checking color at {self.cell_region}')
        img = pyautogui.screenshot(region=self.cell_region)
        img_rgb = img.convert('RGB')

        def within_range(test, check, tolerance):
            if check - tolerance <= test <= check + tolerance:
                return True
            return False

        search_all = False
        if color in (self.BLANK_COLOR_1, self.BLANK_COLOR_2, self.HIDDEN_COLOR_1, self.HIDDEN_COLOR_2):
            search_all = True

        identified_color = []

        for x in range(self.parent.cell_size // 2 - self.POSITION_TOLERANCE, self.parent.cell_size // 2 + self.POSITION_TOLERANCE):  # Checks color within certain x range
            logging.debug(f'X: {x}, Y: {self.parent.cell_size // 2}')
            rgb_pixel = img_rgb.getpixel((x, self.parent.cell_size // 2))
            pixel_color_rgb = zip(rgb_pixel, color)
            color_in_pixel = all(map(lambda x: within_range(x[0], x[1], self.COLOR_TOLERANCE), pixel_color_rgb))
            if color_in_pixel and not search_all:
                return True
            if color_in_pixel and search_all:
                identified_color.append(True)
            if not color_in_pixel and search_all:
                identified_color.append(False)
        return False if not search_all else all(identified_color)


    def update(self):
        if self.color_match(self.HIDDEN_COLOR_1) or self.color_match(self.HIDDEN_COLOR_2):
            self.state = '-'
        elif self.color_match(self.BLANK_COLOR_1) or self.color_match(self.BLANK_COLOR_2):
            self.state = '0'
        elif self.color_match(self.ONE_COLOR):
            self.state = '1'
        elif self.color_match(self.TWO_COLOR):
            self.state = '2'
        elif self.color_match(self.THREE_COLOR):
            self.state = '3'
        elif self.color_match(self.FOUR_COLOR):
            self.state = '4'
        elif self.color_match(self.FIVE_COLOR):
            self.state = '5'
        else:
            logging.debug('Failed to identify color.')
            self.state = 'E'

class MinesweeperSolver():
    """Creates a class that automatically solves Google Minesweeper if it can be found on the primary screen at runtime."""

    # CONSTANTS relating to how the game looks and is designed. These should only be changed if Google changes the game!
    PLAY_BUTTON_IMAGE = im_path('play_button.png')

    # Note: these menu images actually refer to the image of the difficulty button, which is always in the top-left of the menu bar
    MENU_BAR_EASY = im_path('menu_bar_easy.png')
    MENU_BAR_MEDIUM = im_path('menu_bar_medium.png')  # Google defaults to this
    MENU_BAR_HARD = im_path('menu_bar_hard.png')

    MENU_BAR_HEIGHT = 60

    CELL_SIZE_EASY = 45  # in pixels
    CELL_SIZE_MEDIUM = 30
    CELL_SIZE_HARD = 25

    BOARD_SIZE_EASY = (10, 8)  # Board size given as tuple of (x, y) ie. (10, 8) is a 10 x 8 board
    BOARD_SIZE_MEDIUM = (18, 14)
    BOARD_SIZE_HARD = (24, 20)

    # This includes the menu bar
    GAME_REGION_SIZE_EASY = (450, 420)
    GAME_REGION_SIZE_MEDIUM = (540, 480)
    GAME_REGION_SIZE_HARD = (600, 560)

    # This program detects the state of the cell using its distinct color at a specific location.
    # This specific location is found (x, y) relative to the top left corner of each cell:
    # TODO: Find color movements for easy and hard
    EASY_COLOR_MOVEMENT = (None, None)
    MEDIUM_COLOR_MOVEMENT = (16, 14)
    HARD_COLOR_MOVEMENT = (None, None)

    def __init__(self, difficulty = 'medium'):
        """Initializes accounting for difficulty."""
        logging.debug(f'Creating new MinesweeperSolver with {difficulty} diffuculty')

        self.difficulty = difficulty
        self.menu_bar_image = im_path('menu_bar_' + self.difficulty.lower() + '.png')
        self.board = []
        self.board_size = (None, None)  # Gives board size as a tuple of (x, y) AKA (columns, rows) in cells
        self.cell_size = None
        self.menu_region = None
        self.game_region = None
        self.game_region_size = (None, None)  # Given in pixels
        self.first_click = True
        self.color_movement = (None, None)


    def click_play(self):
        """Prepares the solver by bringing up the Minesweeper game if not already present."""
        logging.debug('Clicking play button! If already clicked, nothing should happen.')

        if self.find_menu_bar_region() is not None:  # Searches to see if game is already present on screen
            logging.debug('Play button already clicked!')

        else:
            logging.debug('Menu not present! Looking for play button!')
            play_button_pos = pyautogui.locateCenterOnScreen(self.PLAY_BUTTON_IMAGE, confidence = 0.9, grayscale = True)
            logging.info(f'Play button is located at {play_button_pos}')
            assert play_button_pos is not None, 'Google Minesweeper does not seem to be present on screen'
            pyautogui.click(play_button_pos)


    def find_menu_bar_region(self):
        """Finds the location of the default menu region, regardless of which difficulty it is set to."""
        logging.debug('Searching for menu region')

        if self.menu_region == None:
            self.menu_region = pyautogui.locateOnScreen(self.MENU_BAR_EASY, confidence = 0.9)
        if self.menu_region == None:
            self.menu_region = pyautogui.locateOnScreen(self.MENU_BAR_MEDIUM, confidence = 0.9)
        if self.menu_region == None:
            self.menu_region = pyautogui.locateOnScreen(self.MENU_BAR_HARD, confidence = 0.9)

        logging.debug(f'Menu region is {self.menu_region}')
        return self.menu_region


    def set_difficulty(self):
        """Sets the difficulty according to the call and sets various instance variables dependent on difficulty."""
        logging.debug('Setting various values based off difficulties chosen...')
        assert self.difficulty.lower() in ('easy', 'medium', 'hard'), 'Valid difficulty not chosen!'

        pyautogui.moveTo(pyautogui.center(self.menu_region))  # Moves mouse to center of difficulty region
        pyautogui.click()

        if self.difficulty.lower() == 'easy':
            pyautogui.moveRel(0, 30)  # Appropriate amount of movement to select easy
            pyautogui.click()
            self.board_size = self.BOARD_SIZE_EASY
            self.cell_size = self.CELL_SIZE_EASY
            self.game_region_size = self.GAME_REGION_SIZE_EASY
            self.color_movement = self.EASY_COLOR_MOVEMENT

        elif self.difficulty.lower() == 'hard':
            pyautogui.moveRel(0, 70)  # Appropriate amount of movement to select hard
            pyautogui.click()
            self.board_size = self.BOARD_SIZE_HARD
            self.cell_size = self.CELL_SIZE_HARD
            self.game_region_size = self.GAME_REGION_SIZE_HARD
            self.color_movement = self.HARD_COLOR_MOVEMENT

        else:  # difficulty = medium
            pyautogui.moveRel(0, 45)  # Appropriate amount of movement to select medium
            pyautogui.click()
            self.board_size = self.BOARD_SIZE_MEDIUM
            self.cell_size = self.CELL_SIZE_MEDIUM
            self.game_region_size = self.GAME_REGION_SIZE_MEDIUM
            self.color_movement = self.MEDIUM_COLOR_MOVEMENT


    def find_game_region(self):
        """Finds the game region based off the menu region."""
        logging.debug(self.menu_bar_image)
        self.find_menu_bar_region()
        self.game_region = (self.menu_region[0], self.menu_region[1], *(self.game_region_size))
        logging.debug(f'Game region is {self.game_region}')


    def print_board(self):
        presentable_board = ('\n'.join([''.join(['{:4}'.format(item.state) for item in row]) for row in self.board]))
        logging.debug('Current board:\n' + presentable_board)


    def generate_board(self):
        """Generates a 2D array to represent the actual Minesweeper board."""
        logging.debug('Generating board...')
        self.board = [[MinesweeperCell(self, (x, y)) for x in range(self.board_size[0])] for y in range(self.board_size[1])] # Makes 2D array of MinesweeperCells

        # Assigns to each MinesweeperCell in the 2D array a region on the screen
        for row in self.board:
            cell_height = self.board.index(row)
            for cell in row:
                cell_width = row.index(cell)

                cell.cell_region = (
                    self.menu_region[0] + cell_width * self.cell_size,
                    self.menu_region[1] + self.MENU_BAR_HEIGHT + cell_height * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )

                cell.identify_neighbors()
        self.print_board()


    def update_board(self):
        """Updates each cell in the board to its current state."""
        logging.debug('Updating board!')
        for y in self.board:
            for cell in y:
                cell.update()
        self.print_board()


    def evaluate_board(self):
        pass


    def click_and_flag(self):
        """Flags the 100% cells as determined in evaluate_board() and clicks the 0% cells."""
        logging.debug('Entering clicking and flagging phase!')
        if self.first_click:
            logging.debug('Doing first click on center of screen!')
            pyautogui.click(pyautogui.center(self.game_region))
        else:
            self.first_click = False
            logging.debug('Entering normal phase of clicking and flagging.')


def main():
    """The main control loop"""
    pass
m = MinesweeperSolver('medium')
m.click_play()
m.find_menu_bar_region()
m.set_difficulty()
m.find_game_region()
m.generate_board()
m.click_and_flag()
# m.update_board()

# if __name__ == '__main__':
#     main()
