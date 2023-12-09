# Converts the returned coordinates from the event in the
# The integer 81 would return the string "a8"
# It's reversed and the first character is turned to a letter
def launchpad_to_uci(touch_event):
    letter = chr(int(str(touch_event)[1]) + 96)  # 97 is unicode for the letter "a"
    number = str(touch_event)[0]
    return letter + number


# This converts the uci string "a1" into the x, y values (0, 8)
# Not sure why the LED coordinates start in top left and touch
# Coordinates start in top right
def uci_to_xy(uci):
    return ord(uci[0]) - 97, 9 - int(uci[1])


def uci_to_launchpad(uci):
    return int(str(int(uci[1])) + str(ord(uci[0]) - 96))
