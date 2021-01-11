# Introduction

![GIF of AI in action]()

The GoogleMinesweeperAI-py recognizes the [Google Minesweeper game](https://www.google.com/fbx?fbx=minesweeper) on your screen and then plays it.

######WARNING: this program has only been tested on a 1920 x 1200 screen. It may not work on other screen sizes depending on how the Google Minesweeper application resizes itself.

# Installation

1. First, clone/download the repository. This can be done in a shell of your choice by moving to the directory you desire to have the project in then typing ```git clone https://github.com/pangene/GoogleMinesweeperAI-py```

2. Move into the directory from your shell ```cd GoogleMinesweeperAI-py```

3. Install the required modules (likely in a virtual environment). ```pip install -r requirements.txt```

3. Run the GoogleMinesweeperSolver.py file: ```python3 GoogleMinesweeperSolver.py```

# Detailed Overview

I began this project in Summer 2020, and then got distracted with the upcoming university semester. I then came back to this in Winter 2021, and finished it up. So, be aware, you may wonder why I did things in some ways and the answer is that I forgot how I originally planned on doing them.

First, this program asks you what difficulty of Minesweeper you want to play on. 

Then, it enters the setup phase. The program tries to identify the Google Minesweeper game on your primary monitor. It can do this either through the play button you can see right after typing "Minesweeper" into the Google searchbar, or it can identify the game once play has already been pressed (this is the default if you go to the [Google Minesweeper site](https://www.google.com/fbx?fbx=minesweeper) itself and not typing it into the search bar). It clicks play if it needs to. It sets up some variables based off the difficulty after that, and also picks the difficulty you chose. It then looks for the game region and performs the first click. From there, it begins to simulate the minesweeper game.

The program creates a simulated board (just a list of lists) and populates that list with cell classes. It gives each cell a region on the screen where it physically is and then identifies its neighbors. Then, it updates all cells in the board based off the Minesweeper game. When it updates, it identifies whether the cell is hidden, blank, or a number based off the color. If it fails to do so, the program raises an error. This may occur if you use flux or some program that tints your screen too much for the color to be recognized.

After the setup phase, it enters the event loop. Here, it repeats the process of reading the screen, finding guaranteed safe or mine cells, then clicking them. To speed things up and not search the entire board every time, the solver keeps a list of active cells that have useful information that could be used to solve still-hidden cells. It regularly also checks this active cell list for cells that already have all their neighbors found and deactivates them.

The AI is fairly simplistic. For each active cell, it identifies if the # of hidden neighbor cells == the # of remaining mines. If so, then all these cells are automatically mines. It then flags said mines, updating the neighbors. After, it identifies all active cells with no remaining mines, and clicks on any remaining hidden cells. If an active cell has no remaining hidden cells, it is deactivated. The new clicked cells then become active cells.

This AI fails to reflect all cases. It only works for deterministic cases, and Minesweeper is not deterministic. It will only click or flag a cell if it is guaranteed to be safe or a mine. More complex AI will calculate probabilities and take into account remaining mines. [Read here for more information about that](https://luckytoilet.wordpress.com/2012/12/23/2125/).

If there are no more simple, deterministic cases, the program returns control to the user.

# Improvements

* Speeding up the updating of cells. Each cell has to carefully check a range of positions for colors. This range of positions can likely be narrowed, or can be customized for each color. Although, this would have to take into account differing cell sizes based off difficulty. Multiprocessing can also be useful here to simultaneously update and check cells.

* Developing the AI to calculate probabilities instead. The best Minesweeper AI, while still not perfect, can function in nondeterministic cases by calculating the most-likely cells with mines and clicking those. My AI just freezes.