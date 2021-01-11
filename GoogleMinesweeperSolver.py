"""This module automatically solves the Google Chrome version of Minesweeper.

Author: Gene Pan
Date Began: Aug-02-2020
Last Edited: Jan-11-2021
"""

import os
import time
import logging
import pyautogui
import cv2  # Necessary for pyautogui's confidence, but a refactor can probably make it obsolete
from PIL import Image
pyautogui.PAUSE = 0

# logging.basicConfig(
#     format='%(asctime)s,%(msecs)d %(levelname)-8s [%(name)s:%(filename)s:%(lineno)d] %(message)s',
#     datefmt='%Y-%m-%d:%H:%M:%S',
#     level=logging.DEBUG)

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(asctime)s.%(msecs)03d: [%(lineno)d] %(message)s', datefmt='%H:%M:%S',
    # filename='testlog.log'  # Uncomment to record logging data to a file
)
# logging.disable(logging.info) # uncomment to block debug log messages


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
    TWO_COLOR = (56, 142, 60)
    THREE_COLOR = (211, 47, 47)
    FOUR_COLOR = (155, 85, 159)
    FIVE_COLOR = (254, 144, 3)

    COLOR_TOLERANCE = 60  # Distance in RGB value
    POSITION_TOLERANCE = 5  # how many pixels around center will the color be searched for

    CLICK_WAIT = 0.4  # Time to wait until updating cell after clicking

    FAILURE_LIMIT = 2  # How many times can the color fail to be identified before raising exception


    def __init__(self, ms_solver, coordinate):
        logging.debug(f'Creating cell at {coordinate}')
        self.parent = ms_solver
        self.cell_region = (None, None, None, None)
        self.state = 'U'
        self.color_position = None
        self.coordinate = coordinate  # (x, y) tuple
        self.neighbors = []
        self.mines_remaining = None
        self.center = (None, None)
        self.identification_failures = 0


    def __str__(self):
        return self.state


    def __repr__(self):
        return f'{self.coordinate}'


    def identify_neighbors(self):
        for x in range(self.coordinate[0] - 1, self.coordinate[0] + 2):
            for y in range(self.coordinate[1] - 1, self.coordinate[1] + 2):
                if (x, y) != self.coordinate and 0 <= x < self.parent.board_size[0] and 0 <= y < self.parent.board_size[1]:
                    logging.debug(f'Neighbor for cell at ({self.coordinate[0], self.coordinate[1]}): ({x}, {y})')
                    neighbor = self.parent.board[y][x]
                    self.neighbors.append(neighbor)


    def get_neighbors_of(self, state):
        """Returns a list of neighbor cells that are of the specified state"""
        identified = []
        for neighbor in self.neighbors:
            if neighbor.state == state:
                identified.append(neighbor)
        return identified


    def color_match(self, color):
        # pyautogui.moveTo(x=1000, y=1000)
        logging.info(f'Checking color at {self.coordinate}')
        img = pyautogui.screenshot(region=self.cell_region)
        img_rgb = img.convert('RGB')

        def within_range(test, check, tolerance):
            if check - tolerance <= test <= check + tolerance:
                return True
            return False

        search_all = False  # If it's a number cell, should identify cell as soon as it finds number.
        if color in (self.BLANK_COLOR_1, self.BLANK_COLOR_2, self.HIDDEN_COLOR_1, self.HIDDEN_COLOR_2):
            search_all = True

        identified_color = []

        for x in range(self.parent.cell_size // 2 - self.POSITION_TOLERANCE, self.parent.cell_size // 2 + self.POSITION_TOLERANCE):  # Checks color within certain x range
            logging.debug(f'X: {x}, Y: {self.parent.cell_size // 2}')
            rgb_pixel = img_rgb.getpixel((x, self.parent.cell_size // 2))
            logging.debug(f'RGB: {rgb_pixel}')
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
        """Updates the cell's state."""
        # This looks disgusting and is disgusting
        if self.state == '-' or self.state == 'U':
            if self.color_match(self.HIDDEN_COLOR_1) or self.color_match(self.HIDDEN_COLOR_2):
                self.state = '-'
            elif self.color_match(self.BLANK_COLOR_1) or self.color_match(self.BLANK_COLOR_2):
                self.state = '0'
                self.mines_remaining = 0
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
                img = pyautogui.screenshot('failed_image.png', region=self.cell_region)  # Saves failed image as PNG for debugging
                if self.identification_failures > self.FAILURE_LIMIT:
                    # Instant failure is bad since sometimes, little green animation squares fall from above onto image to cause failure.
                    # Partly accounted for with waiting, but can fall from any cell above self
                    raise Exception('Color Indentification Failed')
                self.identification_failures += 1
                self.update()

        self.update_mines_remaining()

        if self.state not in ('-', 'F') and self.get_neighbors_of('-') and self not in self.parent.active_cells:
            self.parent.active_cells.append(self)


    def update_neighbors(self):
        for neighbor in self.neighbors:
            neighbor.update()


    def update_mines_remaining(self):
        """Updates the number of mines remaining."""
        neighbor_flags_amt = len(self.get_neighbors_of('F'))
        if self.state != '-' and self.state != 'F':
            self.mines_remaining = int(self.state) - neighbor_flags_amt


    def get_flags(self):
        """Returns a list of all neighbor cells that are guaranteed to be flags."""
        self.update_mines_remaining()
        hidden_cells = self.get_neighbors_of('-')
        if self.mines_remaining == len(hidden_cells):
            return hidden_cells
        return []


    def get_safe(self):
        """Returns a list of all neighbor cells that are guaranteed to be safe."""
        self.update_mines_remaining()
        if not self.mines_remaining:
            return [cell for cell in self.neighbors if cell.state == '-']
        return []


    def click(self):
        """Left clicks on own cell region."""
        logging.info(f'Clicking cell at {self.coordinate}')
        pyautogui.click(x=self.center[0], y=self.center[1])
        time.sleep(self.CLICK_WAIT)
        self.update()
        if self.state == '0':
            self.parent.update_board()
        self.update_neighbors()


    def flag(self):
        """Right clicks on own cell region."""
        if self.state != 'F':
            logging.info(f'Flagging cell at {self.coordinate}')
            pyautogui.rightClick(x=self.center[0], y=self.center[1])
            self.state = 'F'
        # self.update_neighbors()


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


    def __init__(self, difficulty = 'medium'):
        """Initializes accounting for difficulty."""
        logging.debug(f'Creating new MinesweeperSolver with {difficulty} diffuculty')

        self.difficulty = difficulty
        self.menu_bar_image = im_path('menu_bar_' + self.difficulty.lower() + '.png')
        self.board = []  # Ideally, this would be a GameState class or something.
        self.board_size = (None, None)  # Gives board size as a tuple of (x, y) AKA (columns, rows) in cells
        self.cell_size = None
        self.menu_region = None
        self.game_region = None
        self.game_region_size = (None, None)  # Given in pixels
        self.active_cells = []


    def click_play(self):
        """Prepares the solver by bringing up the Minesweeper game if not already present."""
        logging.debug('Clicking play button! If already clicked, nothing should happen.')

        self.find_menu_bar_region()

        if self.menu_region:  # Searches to see if game is already present on screen
            logging.debug('Play button already clicked!')
        else:
            logging.debug('Menu not present! Looking for play button!')
            play_button_pos = pyautogui.locateCenterOnScreen(self.PLAY_BUTTON_IMAGE, confidence = 0.9, grayscale = True)
            logging.info(f'Play button is located at {play_button_pos}')
            assert play_button_pos is not None, 'Google Minesweeper does not seem to be present on screen'
            pyautogui.click(play_button_pos)
            self.find_menu_bar_region()


    def find_menu_bar_region(self):
        """Finds the location of the default menu region, regardless of which difficulty it is set to."""
        logging.debug('Searching for menu region')
        if not self.menu_region:
            self.menu_region = pyautogui.locateOnScreen(self.MENU_BAR_EASY, confidence = 0.9)
        if not self.menu_region:
            self.menu_region = pyautogui.locateOnScreen(self.MENU_BAR_MEDIUM, confidence = 0.9)
        if not self.menu_region:
            self.menu_region = pyautogui.locateOnScreen(self.MENU_BAR_HARD, confidence = 0.9)
        logging.debug(f'Menu region is {self.menu_region}')


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

        elif self.difficulty.lower() == 'hard':
            pyautogui.moveRel(0, 70)  # Appropriate amount of movement to select hard
            pyautogui.click()
            self.board_size = self.BOARD_SIZE_HARD
            self.cell_size = self.CELL_SIZE_HARD
            self.game_region_size = self.GAME_REGION_SIZE_HARD

        else:  # difficulty = medium
            pyautogui.moveRel(0, 45)  # Appropriate amount of movement to select medium
            pyautogui.click()
            self.board_size = self.BOARD_SIZE_MEDIUM
            self.cell_size = self.CELL_SIZE_MEDIUM
            self.game_region_size = self.GAME_REGION_SIZE_MEDIUM


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

                cell.center = pyautogui.center(cell.cell_region)

                cell.identify_neighbors()
        self.print_board()


    def update_board(self):
        """Updates each cell in the board to its current state."""
        logging.debug('Updating board!')
        for y in self.board:
            for cell in y:
                cell.update()
        self.print_board()


    def identify_all_safe_moves(self):
        """Returns a tuple of all (flag_moves, safe_moves) for the neighbors of the active cells."""
        flags, safe = [], []
        for cell in self.active_cells[:]:
            logging.info(f'Identifying moves for {cell.coordinate}')
            cell_flags = cell.get_flags()
            cell_safe = cell.get_safe()
            if cell_flags or cell_safe:
                logging.debug(f'Flags: {[cell.coordinate for cell in cell_flags]}, Safe moves: {[cell.coordinate for cell in cell_safe]}')
            flags.extend(cell_flags)
            safe.extend(cell_safe)
        return (flags, safe)


    def perform_all_safe_moves(self, flags, safe):
        """Flags or clicks all cells guaranteed to be either mines or safe respectively."""
        for flag_cell in flags:
            flag_cell.flag()
        for safe_cell in safe:
            safe_cell.click()


    def remove_inactive_cells(self):
        """Removes inactive cells from self.active_cells."""
        for cell in self.active_cells[:]:
            if not cell.get_neighbors_of('-'):
                self.active_cells.remove(cell)


    def first_click(self):
        """Performs the first click to reveal the initial cell plot"""
        logging.debug('Doing first click on center of screen!')
        pyautogui.click(pyautogui.center(self.game_region))


    def set_up(self):
        """Performs all the setup, pre-event_loop functions."""
        self.click_play()
        self.set_difficulty()
        time.sleep(0.1)
        self.find_game_region()
        self.first_click()
        self.generate_board()
        self.update_board()

    def event_loop(self):
        """Enters the repeating phases of reading and clicking cells."""
        logging.info('Entering the event loop.')
        flags, safe = self.identify_all_safe_moves()
        while flags or safe:
            self.perform_all_safe_moves(flags, safe)
            self.remove_inactive_cells()
            flags, safe = self.identify_all_safe_moves()
            self.print_board()


def main():
    print('Pick a difficulty: \n(0) easy, \n(1) medium, \n(2) hard.')
    difficulty = int(input())
    difficulty = ['easy', 'medium', 'hard'][difficulty]
    m = MinesweeperSolver(difficulty)
    m.set_up()
    m.event_loop()
    print('Either the game is over, or the AI can no longer help.')

if __name__ == '__main__':
    main()
