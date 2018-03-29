from game_abc import GameABC

class Game(GameABC):
    def __init__(self, config_str):
        pass

    def init_inputs(self, player):
        return []

    def turn_inputs(self, player):
        return []

    def process_output(self, player, action_str):
        pass

    def is_active(self):
        pass

    def score_game(self):
        pass

    def print_game(self):
        pass
