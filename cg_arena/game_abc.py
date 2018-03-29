from abc import ABC, abstractmethod

class GameABC(ABC):
    @abstractmethod
    def __init__(self, config_str):
        ...

    @abstractmethod
    def init_inputs(self, player):
        ...

    @abstractmethod
    def turn_inputs(self, player):
        ...

    @abstractmethod
    def process_output(self, player, action_str):
        ...

    @abstractmethod
    def is_active(self):
        ...

    @abstractmethod
    def score_game(self):
        pass

    @abstractmethod
    def print_game(self):
        pass
