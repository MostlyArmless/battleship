# Mike Thiem, Oct 23 2017
import pygame
import time
import random
import math
from matplotlib import colors as mcolors
import os

# Initialize the pygame engine
pygame.init()

# Initialize the pygame sound system and load the sound files we'll be using
pygame.mixer.init()
cwd = os.getcwd()
sounds = {
    "hit": pygame.mixer.Sound(cwd + "\\explosion.wav"),
    "miss": pygame.mixer.Sound(cwd + "\\splash.wav"),
    "buzzer": pygame.mixer.Sound(cwd + "\\buzzer.wav"),
}


def norm_to_range(x, old_range, new_range):

    # Normalize to [0,1] first
    old_min = min(old_range)
    old_max = max(old_range)
    x_new = (x - old_min) / (old_max - old_min)

    # Scale if necessary
    new_max = max(new_range)
    new_min = min(new_range)
    if new_max != 1 or new_min != 0:
        scale_range = new_max - new_min
        x_scaled = (x_new * scale_range) + new_min
        return x_scaled
    else:
        return x_new


# Set up colors as a dictionary so we can refer to them by name.
colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)
# Convert all the hex colors values to rgba tuples
for key, value in colors.items():
    rgb_tuple = mcolors.to_rgba(value)
    c = []
    for t in rgb_tuple:
        c.append(norm_to_range(t, old_range=[0, 1], new_range=[0, 255]))
    colors[key] = c

# Name some colors after their purposes in our game
colors["empty"] = colors["lightblue"]
colors["miss"] = colors["white"]
colors["hit"] = colors["red"]
colors["selected"] = colors["green"]
colors["boat"] = colors["gray"]

# Define the display size
display_width = 800
display_height = 600
gameDisplay = pygame.display.set_mode((display_width, display_height))

game_phases = {"setup": 1, "play": 2}

# boats = {"carrier":5,
# "battleship":}


def quit_screen():
    # Clear the screen and display a quit message
    gameDisplay.fill(colors["white"])
    fullscreen_message_display("Quitting.", 0.5)


class armada:
    def __init__(self):
        self.carrier = boat(5)
        self.battleship = boat(4)
        self.submarine = boat(3)
        self.destroyer = boat(3)
        self.patrol_boat = boat(2)


# Number of boats placed, Size of next boat that will be placed
cursor_sizes = {0: 5, 1: 4, 2: 3, 3: 3, 4: 2, 5: 1}

global num_boats_to_place
num_boats_to_place = 5


class grid:
    # Used to draw both the player's own board and the guessing board

    def check_cell_contents(self, coordinates_to_check, contents_to_check):
        # Returns True if any coordinate tuples in the provided list contain the specified contents
        for coord in coordinates_to_check:
            if self.cells[coord[0]][coord[1]].contents == colors[contents_to_check]:
                return True
        return False

    def place_cursor(self, cursor_coordinates, contents):
        for coord in cursor_coordinates:
            self.cells[coord[0], coord[1]].contents = curso

    def init_boat_cursor(self, start_coord=(4, 4)):
        # Place a new boat

        start_row = start_coord[0]
        start_col = start_coord[1]
        cell_outside_grid = True
        while cell_outside_grid:
            # Based on the cursor orientation, extend the cursor down/right by the boat_size
            if self.cursor_orientation == "vertical":
                cursor_rows = [
                    x + 1 for x in range(start_row, start_row + self.cursor_size + 1)
                ]
                cursor_cols = [start_col] * self.cursor_size

            elif self.cursor_orientation == "horizontal":
                cursor_rows = [start_row] * self.cursor_size
                cursor_cols = [
                    x + 1 for x in range(start_col, start_col + self.cursor_size + 1)
                ]

            # Zip together the coordinates to check into a list
            cursor_coordinates = list(zip(cursor_rows, cursor_cols))

            # Check if this cursor is inside the grid
            cell_outside_grid = False
            for c in cursor_coordinates:
                for xy in c:
                    if xy < 0 or xy > self.num_cells - 1:
                        cell_outside_grid = True

        self.cursor_cells = cursor_coordinates

    def __init__(
        self, player_ID, x, y, board_size=500, is_active=False, board_type="own"
    ):
        # Constructor for the grid class

        # Check inputs
        self.num_cells = 10
        self.board_size = board_size
        self.cell_size = math.floor(self.board_size / self.num_cells * 0.8)
        self.line_thickness = (self.board_size - (self.cell_size * self.num_cells)) / (
            self.num_cells + 1
        )
        self.board_x = x
        self.board_y = y
        self.player_ID = player_ID
        self.is_active = is_active
        self.cells = self.create_cell_array()
        self.cursor_orientation = "vertical"
        self.num_boats_placed = 0
        self.board_type = board_type

        if self.board_type == "own":
            self.num_boats_placed = 0
            self.num_hits_taken = 0
        else:
            self.num_boats_placed = 5
            self.num_hits_taken = None

        self.cursor_size = cursor_sizes[self.num_boats_placed]

        # List of tuples, each with x,y cell coordinates (not in pixel but in cells)
        self.init_boat_cursor()
        self.cursor_color = colors["selected"]

    def create_cell_array(self):
        # Initialize a 2d list to put the cell objects into
        cells = [
            [
                cell(x=0, y=0, w=self.cell_size, h=self.cell_size)
                for i in range(self.num_cells)
            ]
            for j in range(self.num_cells)
        ]
        # Set up the coordinates of each of the cells
        for iRow in range(0, self.num_cells):
            y = self.board_y + self.line_thickness * (iRow + 1) + self.cell_size * iRow
            for iCol in range(0, self.num_cells):
                x = (
                    self.board_x
                    + self.line_thickness * (iCol + 1)
                    + self.cell_size * iCol
                )
                cells[iRow][iCol].rect.x = x
                cells[iRow][iCol].rect.y = y

        return cells

    def draw(self):
        # Only draw the grid if it's this player's turn.
        if self.player_ID == player_turn:
            # Draw the black background of the game grid
            pygame.draw.rect(
                gameDisplay,
                colors["black"],
                [self.board_x, self.board_y, self.board_size, self.board_size],
            )
            # Draw all of the cells in the grid
            for iRow in range(len(self.cells)):
                for iCol in range(len(self.cells[iRow])):
                    c = self.cells[iRow][iCol]
                    if self.is_active and (iRow, iCol) in self.cursor_cells:
                        this_cell_color = self.cursor_color
                    else:
                        this_cell_color = c.contents

                    pygame.draw.rect(gameDisplay, this_cell_color, c.rect)
        else:
            return

    def rotate_cursor(self):
        if self.cursor_size == 1:
            # Orientation has no meaning when cursor is only one cell
            return

        else:
            if self.cursor_orientation == "horizontal":
                # Go from horizontal to vertical
                self.cursor_orientation = "vertical"
            else:
                # Go from vertical to horizontal
                self.cursor_orientation = "horizontal"

            # Keep the same origin but extend in the opposite direction
            old_cursor = self.cursor_cells
            self.init_boat_cursor()

    def attack(self, enemy_grid):
        # Check if the selected cell contains an existing guess
        if self.check_cell_contents(
            self.cursor_cells, "hit"
        ) or self.check_cell_contents(self.cursor_cells, "miss"):
            # User has already attacked this cell, don't let them attack it again.cursor_cells
            attack_is_valid = False
            print("INVALID ATTACK")
            sounds["buzzer"].play()

        else:
            attack_is_valid = True
            # This cell is blank, so we can attack it. Now we need to check the enemy's board to see if the target cell contains a boat
            iRow = self.cursor_cells[0][0]
            iCol = self.cursor_cells[0][1]

            if enemy_grid.check_cell_contents(self.cursor_cells, "boat"):
                # Hit! Mark this cell on our grid as a hit.
                sounds["hit"].play()
                self.cells[iRow][iCol].contents = colors["hit"]
                enemy_grid.cells[iRow][iCol].contents = colors["hit"]
                enemy_grid.num_hits_taken += 1
                persistent_message_display("HIT!", self.cells[iRow][iCol].rect.center)
                print("HIT")

            else:
                # Miss!
                sounds["miss"].play()
                self.cells[iRow][iCol].contents = colors["miss"]
                enemy_grid.cells[iRow][iCol].contents = colors["miss"]
                persistent_message_display("miss", self.cells[iRow][iCol].rect.center)

        return attack_is_valid

    def cursor_click(self, enemy_grid):
        # Click the cursor
        click_is_valid = False
        if game_phase == game_phases["setup"]:
            # Check for collision with existing boat
            if self.check_cell_contents(self.cursor_cells, "boat") == True:
                # There's already a boat here, we can't place it
                print("BAD SPOT FOR BOAT")
                return click_is_valid
            else:
                click_is_valid = True
                print("Layin down a boat")
                for c in self.cursor_cells:
                    self.cells[c[0]][c[1]].contents = colors["boat"]

                self.num_boats_placed += 1
                self.cursor_size = cursor_sizes[self.num_boats_placed]
                self.init_boat_cursor()

        elif game_phase == game_phases["play"]:
            # Check whether their guess is on a blank spot or not
            click_is_valid = self.attack(enemy_grid)

        return click_is_valid

    def move_cursor(self, row_increment, col_increment, cursor_move_complete):
        # Move the selected cell by the specified amount
        new_cursor_cells = []
        old_cursor_cells = self.cursor_cells
        cursor_move_legal = True

        if cursor_move_complete:
            print(cursor_move_complete)
            return cursor_move_complete

        else:
            for c in self.cursor_cells:

                new_row = c[0] + row_increment
                if new_row < 0 or new_row > self.num_cells - 1:
                    cursor_move_legal = False

                new_col = c[1] + col_increment
                if new_col < 0 or new_col > self.num_cells - 1:
                    cursor_move_legal = False

                if cursor_move_legal:
                    # print(f'new cursor cell = {new_row},{new_col}')
                    new_cursor_cells.append((new_row, new_col))

            if cursor_move_legal:
                self.cursor_cells = new_cursor_cells
            else:
                self.cursor_cells = old_cursor_cells

            # Consider the cursor move "complete" whether or not it was legal.
            # This is just a debouncing technique.
            cursor_move_complete = True
            return cursor_move_complete


def text_objects(text, font):
    # Render given text onto a pygame surface
    textSurface = font.render(text, True, colors["black"])
    return textSurface, textSurface.get_rect()


def message_display(text, center, font_size=12, font="freesansbold.ttf"):
    font_params = pygame.font.Font(font, font_size)
    TextSurface, TextRect = text_objects(text, font_params)
    TextRect.center = center
    gameDisplay.blit(TextSurface, TextRect)


def persistent_message_display(
    text, center, font_size=12, font="freesansbold.ttf", duration=1
):
    message_display(text, center, font_size, font)
    pygame.display.update()
    if duration > 0:
        time.sleep(duration)


def fullscreen_message_display(text, duration=2):
    # Display a message on the screen
    message_display(
        text, center=((display_width / 2), (display_height / 2)), font_size=115
    )

    pygame.display.update()
    if duration > 0:
        time.sleep(duration)


# Window title
pygame.display.set_caption("Battleship")

# Define the game's clock
clock = pygame.time.Clock()
targetFps = 60


class cell:
    def __init__(self, x=0, y=0, vx=0, vy=0, w=40, h=40):
        self.rect = pygame.Rect(x, y, w, h)
        self.contents = colors["empty"]


def game_loop():
    # The primary game loop.
    global player_turn
    player_turn = 1  # Since player one always goes first
    global game_phase
    total_boat_cells = 5 + 4 + 3 + 3 + 2
    game_phase = game_phases["setup"]

    # Instantiate the objects
    board_size = 255
    horizontal_grid_separation = 50
    vertical_grid_separation = 10
    left_margin = 50
    top_margin = 50

    grid_player1_enemy = grid(
        player_ID=1,
        x=left_margin,
        y=top_margin,
        board_size=board_size,
        is_active=False,
        board_type="enemy",
    )

    grid_player1_own = grid(
        player_ID=1,
        x=grid_player1_enemy.board_x,
        y=grid_player1_enemy.board_y
        + grid_player1_enemy.board_size
        + vertical_grid_separation,
        board_size=board_size,
        is_active=True,
        board_type="own",
    )

    grid_player2_enemy = grid(
        player_ID=2,
        x=grid_player1_enemy.board_x
        + grid_player1_enemy.board_size
        + horizontal_grid_separation,
        y=top_margin,
        board_size=board_size,
        is_active=False,
        board_type="enemy",
    )

    grid_player2_own = grid(
        player_ID=2,
        x=grid_player2_enemy.board_x,
        y=grid_player1_own.board_y,
        board_size=board_size,
        is_active=False,
        board_type="own",
    )

    gameExit = False
    # Variables for tracking which direction to move the cursor
    row_increment = 0
    col_increment = 0
    cursor_move_complete = False
    fullscreen_message_display("Player 1, place your boats")
    active_grid = grid_player1_own
    enemy_grid = grid_player2_own
    while not gameExit:
        click_is_valid = False
        # Interpret the actions that have occurred this clock tick
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    cursor_move_complete = False
                    cursor_move_complete = active_grid.move_cursor(0, -1, False)
                elif event.key == pygame.K_RIGHT:
                    cursor_move_complete = False
                    cursor_move_complete = active_grid.move_cursor(0, 1, False)
                elif event.key == pygame.K_UP:
                    cursor_move_complete = False
                    cursor_move_complete = active_grid.move_cursor(-1, 0, False)
                elif event.key == pygame.K_DOWN:
                    cursor_move_complete = False
                    cursor_move_complete = active_grid.move_cursor(1, 0, False)
                elif event.key == pygame.K_ESCAPE:
                    gameExit = True
                elif event.key == pygame.K_r:
                    active_grid.rotate_cursor()
                elif event.key == pygame.K_RETURN:
                    # Pass a reference to the enemy's grid to be used to determine if an attack hits or not
                    click_is_valid = active_grid.cursor_click(enemy_grid)

            if event.type == pygame.KEYUP:
                if event.key in [
                    pygame.K_LEFT,
                    pygame.K_RIGHT,
                    pygame.K_DOWN,
                    pygame.K_UP,
                ]:
                    cursor_move_complete = True

                if event.key == pygame.K_SPACE:
                    click_cell = False

            if event.type == pygame.QUIT:
                gameExit = True

        # Allow active player to move the cursor
        if game_phase == game_phases["setup"]:
            if player_turn == 1:
                active_grid = grid_player1_own
            elif player_turn == 2:
                active_grid = grid_player2_own

        elif game_phase == game_phases["play"]:
            if player_turn == 1:
                active_grid = grid_player1_enemy
                enemy_grid = grid_player2_own
            elif player_turn == 2:
                active_grid = grid_player2_enemy
                enemy_grid = grid_player1_own

        # Draw next frame
        gameDisplay.fill(colors["white"])
        grid_player1_enemy.draw()
        grid_player1_own.draw()
        message_display(
            "Player 1",
            center=(
                grid_player1_enemy.board_x + grid_player1_enemy.board_size / 2,
                top_margin / 2,
            ),
        )

        grid_player2_enemy.draw()
        grid_player2_own.draw()
        message_display(
            "Player 2",
            center=(
                grid_player2_enemy.board_x + grid_player2_enemy.board_size / 2,
                top_margin / 2,
            ),
        )

        # Update game phase & player turn
        if game_phase == game_phases["setup"]:
            if player_turn == 1 and active_grid.num_boats_placed == num_boats_to_place:
                # Player 1 is finished setup, let player 2 set up
                player_turn = 2
                active_grid.is_active = False
                active_grid = grid_player2_own
                active_grid.is_active = True
                fullscreen_message_display("Player 2, place your boats")

            elif (
                player_turn == 2 and active_grid.num_boats_placed == num_boats_to_place
            ):
                # Player 2 finished their setup as well, so now we transition into the play phase
                player_turn = 1
                active_grid.is_active = False
                active_grid = grid_player1_enemy
                active_grid.is_active = True
                game_phase = game_phases["play"]

        elif game_phase == game_phases["play"]:
            if click_is_valid:
                if player_turn == 1:
                    player_turn = 2

                    active_grid.is_active = False
                    active_grid = grid_player2_enemy
                    active_grid.is_active = True
                    enemy_grid = grid_player1_own

                else:
                    player_turn = 1

                    active_grid.is_active = False
                    active_grid = grid_player1_enemy
                    active_grid.is_active = True
                    enemy_grid = grid_player2_own

            # Check end-game condition
            if grid_player1_own.num_hits_taken == total_boat_cells:
                # Player 1 has lost
                fullscreen_message_display("Player 2 wins!", 5)
                gameExit = True

            if grid_player2_own.num_hits_taken == total_boat_cells:
                # Player 2 has lost
                fullscreen_message_display("Player 1 wins!", 5)
                gameExit = True

        # Update screen contents now that we've redrawn
        pygame.display.update()

        # Advance the game clock
        clock.tick(targetFps)


# Run the game
game_loop()
# Show quit screen
quit_screen()
pygame.display.update()
clock.tick(targetFps)
# Quit pygame
pygame.quit()
# Quit python
quit()
