class InvalidMoveException(Exception):
    def __init__(self, move, valid_moves):
        self.message = f"Invalid move, {move} not in {str(valid_moves)}"
        super().__init__(self.message)