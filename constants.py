OUTPUT_DIR = "/Users/randy/Documents/Saved_Games"

# Color Constants
OFF = (0, 0, 0)
ORANGE = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
PURPLE = (255, 0, 255)
BLACK_SPACE_COLOR = (0, 0, 30)
WHITE_SPACE_COLOR = (5, 5, 3)


# Buttons/Spaces
UNDO_BUTTON = 60
NEW_GAME_BUTTON = 30

WHITE_TURN_BUTTON = 19
BLACK_TURN_BUTTON = 89

BLACKs_WIN_LIGHTS = [59, 69, 79, 89]
WHITE_WIN_LIGHTS = [19, 29, 39, 49]

BLACK_SPACES = [
    int(str(x) + str(y))
    for x in range(1, 9)
    for y in range(1, 9)
    if (y % 2 == 0 and x % 2 == 0) or (y % 2 != 0 and x % 2 != 0)
]
WHITE_SPACES = [
    int(str(x) + str(y))
    for x in range(1, 9)
    for y in range(1, 9)
    if int(str(x) + str(y)) not in BLACK_SPACES
]
