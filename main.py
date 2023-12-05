from launchpad_board import LaunchPadBoard

board = LaunchPadBoard()
while True:
    event = board.poll_for_event()
    if event:
        print(event)
